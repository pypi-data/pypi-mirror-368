import ssl
from typing import Dict, List
from celery import Celery

from ..redis.connection import RedisInstance
from .task import Task


__all__ = ("Worker",)


class Worker:
    _celery: Dict = {
        "name": "dt_celery_app",
        "task_serializer": "json",
        "result_serializer": "json",
        "timezone": "America/Los_Angeles",
        "task_track_started": True,
        "result_persistent": True,
        "worker_prefetch_multiplier": 1,
        "broker": None,
        "backend": None,
    }
    _celery_conf: Dict = {
        "broker_transport_options": {"global_keyprefix": "celery-broker:"},
        "result_backend_transport_options": {"global_keyprefix": "celery-backend:"},
        "enable_utc": False,
        "broker_connection_retry": True,
        "broker_connection_max_retries": 0,
        "broker_connection_retry_on_startup": True,
        "result_expires": 3600,
        "task_routes": {},
        "beat_schedule": {},
        "beat_max_loop_interval": 300,
        "redbeat_redis_url": None,
        "beat_scheduler": "redbeat.RedBeatScheduler",
        "redbeat_key_prefix": "celery-beat:",
        "redbeat_lock_key": "celery-beat::lock",
        "ONCE": {
            'backend': 'celery_once.backends.Redis',
            'settings': {
                'default_timeout': 60 * 60
            }
        }
    }
    _discovered_task: List[str] = []

    def set_task(self, task: Task):
        self._celery_conf["task_routes"] = task.get_tasks_routes()
        self._celery_conf["beat_schedule"] = task.get_periodic_tasks()
        self._discovered_task = task.get_tasks()
        return self

    def set_redis(self, redis_instance: RedisInstance):
        redis_url = redis_instance.get_redis_url()
        self._celery["broker"] = redis_url
        self._celery["backend"] = redis_url
        self._celery_conf["redbeat_redis_url"] = redis_url
        self._celery_conf["ONCE"]['settings']['url'] = redis_url

        if redis_url.startswith("rediss"):
            self._celery["broker_use_ssl"] = {"ssl_cert_reqs": ssl.CERT_NONE}
            self._celery["redis_backend_use_ssl"] = {"ssl_cert_reqs": ssl.CERT_NONE}

        return self

    def set_name(self, name: str):
        self._celery["main"] = name
        return self

    def set_timezone(self, timezone: str):
        self._celery["timezone"] = timezone
        return self

    def set_task_serializer(self, task_serializer: str):
        self._celery["task_serializer"] = task_serializer
        return self

    def set_result_serializer(self, result_serializer: str):
        self._celery["result_serializer"] = result_serializer
        return self

    def set_track_started(self, value: bool):
        self._celery["task_track_started"] = value
        return self

    def set_result_persistent(self, value: bool):
        self._celery["result_persistent"] = value
        return self

    def set_worker_prefetch_multiplier(self, number: int):
        self._celery["worker_prefetch_multiplier"] = number
        return self

    def set_broker_prefix(self, prefix: str):
        self._celery_conf["broker_transport_options"]["global_keyprefix"] = f"{prefix}:"
        return self

    def set_backend_prefix(self, prefix: str):
        self._celery_conf["result_backend_transport_options"][
            "global_keyprefix"
        ] = f"{prefix}:"
        return self

    def set_redbeat_key_prefix(self, prefix: str):
        self._celery_conf["redbeat_key_prefix"] = f"{prefix}:"
        return self

    def set_redbeat_lock_key(self, redbeat_lock_key: str):
        self._celery_conf["redbeat_lock_key"] = redbeat_lock_key
        return self

    def set_enable_utc(self, value: bool):
        self._celery_conf["enable_utc"] = value
        return self

    def set_broker_connection_max_retries(self, value: int):
        self._celery_conf["broker_connection_max_retries"] = value
        return self

    def set_broker_connection_retry_on_startup(self, value: bool):
        self._celery_conf["broker_connection_retry_on_startup"] = value
        return self

    def set_result_expires(self, result_expires: int):
        self._celery_conf["result_expires"] = result_expires
        return self

    def set_once_default_timeout(
        self, default_timeout: int
    ):
        self._celery_conf["ONCE"]["settings"]["default_timeout"] = default_timeout
        return self

    def set_once_blocking(
        self, blocking: bool
    ):
        self._celery_conf["ONCE"]["settings"]["blocking"] = blocking
        return self

    def set_once_blocking_timeout(
        self, blocking_timeout: int
    ):
        self._celery_conf["ONCE"]["settings"]["blocking_timeout"] = blocking_timeout
        return self

    def create(self) -> Celery:
        celery_app = Celery(**self._celery)
        celery_app.conf.update(self._celery_conf)
        celery_app.autodiscover_tasks(self._discovered_task)
        return celery_app
