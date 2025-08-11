import json
from typing import Dict
from dataclasses import dataclass

from ..core.retry import retry_wrapper
from .connection import RedisInstance


__all__ = (
    "Message",
    "Sender",
)


@dataclass
class Message:
    name: str
    body: Dict

    def get_json_encoded(self):
        return {"name": self.name, "body": json.dumps(self.body, default=str)}


class Sender:

    def __init__(self, redis_instance: RedisInstance):
        self._channels = []
        self._redis_instance = redis_instance
        self._redis_client = self._redis_instance.get_redis_client()

    def register_channel(self, channel_name: str):
        self._channels.append(channel_name)

    @retry_wrapper()
    def send_message(self, channel: str, message: Message):
        self._redis_client.xadd(channel, message.get_json_encoded())
