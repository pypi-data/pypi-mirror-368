from typing import List, Dict, Sequence, Tuple
from celery.schedules import crontab
from datetime import timedelta


__all__ = ("Task",)


class Task:
    _tasks: List[str] = []
    _tasks_routes: Dict = {}
    _periodic_tasks: Dict = {}

    def _register_task_route(self, route: str):
        self._tasks.append(route)
        return self

    def register(self, route: str, queue: str | None = None):
        self._register_task_route(route=route)
        task_dict = {}
        if queue:
            task_dict["queue"] = queue

        self._tasks_routes[route] = task_dict
        return self

    def bulk_register(self, routes: Sequence[str], queue: str | None = None):
        for route in routes:
            self.register(route=route, queue=queue)
        return self

    def register_periodic_task(
        self, route: str, schedule: crontab | timedelta, queue: str | None = None, *args
    ):
        self.register(route=route, queue=queue)
        self._periodic_tasks[route] = {
            "task": route,
            "schedule": schedule,
            "args": args,
        }
        return self

    def bulk_register_periodic_task(
        self,
        tasks: Sequence[Tuple[str, crontab | timedelta, Sequence]],
        queue: str | None = None,
    ):
        for route, schedule, args in tasks:
            self.register_periodic_task(
                route=route, schedule=schedule, queue=queue, *args
            )
        return self

    def get_tasks(self) -> list[str]:
        return self._tasks

    def get_tasks_routes(self) -> dict:
        return self._tasks_routes

    def get_periodic_tasks(self) -> dict:
        return self._periodic_tasks
