import json
import time
from typing import Dict, List, Callable

from ..log import footprint
from ..core.exception import exception_to_dict
from ..core.retry import retry_wrapper
from .connection import RedisInstance


__all__ = ("Consumer",)


class Consumer:
    def __init__(self, redis_instance: RedisInstance, consumer_name: str):
        self.consumer_name: str = consumer_name
        self._handlers: Dict[str, List] = {}
        self._channels = []
        self._redis_instance = redis_instance
        self._redis_client = self._redis_instance.get_redis_client()

    def _consumer_group_exists(self, channel_name: str, consumer_group: str) -> bool:
        try:
            groups = self._redis_client.xinfo_groups(channel_name)
            return any(
                group["name"].decode("utf-8") == consumer_group for group in groups
            )
        except:
            return False

    def register_channel(
        self,
        channel_name: str,
        consumers: List[str] | None = None,
        message_cleanup: bool = False,
        read_messages: bool = False,
    ):
        """
        Registers a channel and its consumers, optionally starting message consumption automatically.
        """
        controller = f"{__name__}.Consumer.register_channel"
        if consumers is None:
            consumers = []

        consumer_group = f"{channel_name}_consumer_group"
        if not self._consumer_group_exists(channel_name, consumer_group):
            try:
                self._redis_client.xgroup_create(
                    channel_name, consumer_group, "$", mkstream=True
                )
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Error creating consumer group",
                    message=f"Error creating consumer group {consumer_group} for channel {channel_name}.",
                    controller=controller,
                    payload=exception_to_dict(e),
                )

        self._channels.append(
            (channel_name, consumer_group, consumers, message_cleanup, read_messages)
        )
        self._handlers[channel_name] = []
        return self

    def register_handler(
        self,
        channel_name: str,
        handler_func: Callable,
    ):
        self._handlers[channel_name].append(handler_func)
        return self

    @retry_wrapper()
    def consume_messages(self, channel: str, consumer_group: str, block_time: float):
        """
        Reads and processes messages for a specific consumer group in a channel.
        """
        controller = f"{__name__}.Consumer.consume_messages"
        try:
            messages = self._redis_client.xreadgroup(
                consumer_group,
                self.consumer_name,
                {channel: ">"},
                block=block_time * 1000,
                count=1,
            )

            for message in messages:
                stream_name, message_data = message
                message_id, message_content = message_data[0]

                name = message_content.get(b"name")
                body = message_content.get(b"body")

                if name and body:
                    name = name.decode("utf-8") if isinstance(name, bytes) else name
                    body = (
                        json.loads(body.decode("utf-8"))
                        if isinstance(body, bytes)
                        else body
                    )

                    for handler in self._handlers.get(channel, []):
                        try:
                            handler(name=name, payload=body)
                        except Exception as e:
                            footprint.leave(
                                log_type="error",
                                message="We faced an error while we want to read a message",
                                controller=controller,
                                subject="Consuming Message Error",
                                payload={
                                    "error": exception_to_dict(e),
                                    "handler": handler.__name__,
                                    "name": name,
                                    "body": body,
                                },
                            )

                    self._redis_client.xack(channel, consumer_group, message_id)

        except Exception as e:
            footprint.leave(
                log_type="error",
                message=f"Error consuming messages from channel {channel}",
                controller=controller,
                subject="Consuming Messages Error",
                payload={
                    "error": exception_to_dict(e),
                },
            )

    def persist_consume_messages(
        self, channel: str, consumer_group: str, rest_time: float, block_time: float
    ):
        while True:
            self.consume_messages(
                channel=channel, consumer_group=consumer_group, block_time=block_time
            )
            if rest_time > 0:
                time.sleep(rest_time)

    def consume_all_channels(self, block_time: float):
        for channel_name, consumer_group, _, _, read_messages in self._channels:
            if read_messages:
                self.consume_messages(
                    channel=channel_name,
                    consumer_group=consumer_group,
                    block_time=block_time,
                )

    def persist_consume_all_channels(self, rest_time: float, block_time: float):
        while True:
            self.consume_all_channels(block_time=block_time)
            if rest_time > 0:
                time.sleep(rest_time)

    @retry_wrapper()
    def clean_up_consumed_messages(self):
        """
        Deletes messages from streams that have been fully processed by all consumers in a group.
        """
        controller = f"{__name__}.Consumer.clean_up_consumed_messages"
        for channel_name, _, consumers, message_cleanup, _ in self._channels:
            if not message_cleanup:
                continue

            try:
                messages = self._redis_client.xrange(channel_name)
                messages_to_delete = []

                for message_id, _ in messages:
                    acknowledged_consumers = self.get_acknowledged_consumer_names(
                        channel=channel_name, message_id=message_id
                    )
                    if isinstance(acknowledged_consumers, list) and (
                        set(acknowledged_consumers) >= set(consumers)
                    ):
                        messages_to_delete.append((message_id, acknowledged_consumers))

                if messages_to_delete:
                    self._redis_client.xdel(
                        channel_name, *[item[0] for item in messages_to_delete]
                    )
                    footprint.leave(
                        log_type="info",
                        message=f"Deleted {len(messages_to_delete)} messages from {channel_name}.",
                        controller=controller,
                        subject="Cleaning up messages",
                        payload={"messages": messages_to_delete},
                    )

            except Exception as e:
                footprint.leave(
                    log_type="error",
                    message=f"Error cleaning up messages in channel {channel_name}",
                    controller=controller,
                    subject="Cleaning up messages Error",
                    payload={
                        "error": exception_to_dict(e),
                    },
                )

    def get_acknowledged_consumer_names(
        self, channel: str, message_id: str
    ) -> list[str]:
        """
        Retrieves a list of consumers who have acknowledged a given message ID.
        """
        controller = f"{__name__}.Consumer.get_acknowledged_consumer_names"
        acknowledged_consumers = set()

        try:
            groups = self._redis_client.xinfo_groups(channel)

            for group in groups:
                group_name = (
                    group["name"].decode()
                    if isinstance(group["name"], bytes)
                    else group["name"]
                )

                # Fetch all consumers in the group
                consumers_info = self._redis_client.xinfo_consumers(channel, group_name)
                all_consumers = {
                    (
                        consumer["name"].decode()
                        if isinstance(consumer["name"], bytes)
                        else consumer["name"]
                    )
                    for consumer in consumers_info
                }

                # Fetch detailed pending messages for this group
                pending_messages = self._redis_client.xpending_range(
                    channel, group_name, "-", "+", 100
                )

                # Consumers with this message still pending
                pending_consumers = {
                    (
                        msg["consumer"].decode()
                        if isinstance(msg["consumer"], bytes)
                        else msg["consumer"]
                    )
                    for msg in pending_messages
                    if msg["message_id"] == message_id
                }

                # Acknowledged consumers = all consumers - pending consumers
                acknowledged_consumers.update(all_consumers - pending_consumers)

            return list(acknowledged_consumers)

        except Exception as e:
            footprint.leave(
                log_type="error",
                message=f"Error retrieving acknowledged consumers for message {message_id} in channel {channel}",
                controller=controller,
                subject="Get consumers of a message",
                payload={
                    "error": exception_to_dict(e),
                },
            )
            return None
