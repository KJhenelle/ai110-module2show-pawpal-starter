from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum


class TaskType(Enum):
    WALK = "walk"
    FEEDING = "feeding"
    MEDS = "meds"
    ENRICHMENT = "enrichment"
    GROOMING = "grooming"


class Priority(Enum):
    HIGH = 3
    MEDIUM = 2
    LOW = 1


@dataclass
class TimeSlot:
    start: time
    end: time

    def duration_minutes(self) -> int:
        pass

    def overlaps(self, other: TimeSlot) -> bool:
        pass


@dataclass
class Task:
    title: str
    type: TaskType
    duration_minutes: int
    priority: Priority
    preferred_time: TimeSlot | None = None
    is_completed: bool = False

    def mark_complete(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass


@dataclass
class Owner:
    name: str
    email: str
    available_minutes_per_day: int
    pets: list[Pet] = field(default_factory=list)

    def save_info(self) -> None:
        pass

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> list[Task]:
        pass


@dataclass
class ScheduledItem:
    task: Task
    pet: Pet
    slot: TimeSlot
    reason: str


@dataclass
class DailyPlan:
    date: date
    items: list[ScheduledItem] = field(default_factory=list)
    unscheduled: list[Task] = field(default_factory=list)

    def add_item(self, task: Task, slot: TimeSlot, reason: str) -> None:
        pass

    def total_minutes(self) -> int:
        pass


@dataclass
class Scheduler:
    owner: Owner
    availability: list[TimeSlot] = field(default_factory=list)

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        pass

    def schedule_tasks(self) -> DailyPlan:
        pass

    def explain_choices(self, plan: DailyPlan) -> str:
        pass
