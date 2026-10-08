from __future__ import annotations

import json
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


class Frequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


def _minutes(t: time) -> int:
    return t.hour * 60 + t.minute


def _to_time(minutes: int) -> time:
    return time(minutes // 60, minutes % 60)


@dataclass(frozen=True)
class TimeSlot:
    """Immutable so the scheduler can split windows without mutating shared data."""

    start: time
    end: time

    def __post_init__(self) -> None:
        """Reject slots whose end is not after their start."""
        if self.end <= self.start:
            raise ValueError("TimeSlot end must be after start")

    def duration_minutes(self) -> int:
        """Length of the slot in minutes."""
        return _minutes(self.end) - _minutes(self.start)

    def overlaps(self, other: TimeSlot) -> bool:
        """True if this slot shares any time with `other`."""
        return self.start < other.end and other.start < self.end


@dataclass
class Task:
    title: str
    # Excluded from repr/eq: Pet.tasks points back here, which would recurse forever.
    pet: Pet = field(repr=False, compare=False)
    type: TaskType
    duration_minutes: int
    priority: Priority
    frequency: Frequency = Frequency.DAILY
    preferred_time: TimeSlot | None = None
    # ONCE: the day it is due. WEEKLY: any date on the weekday it repeats.
    # None means it is due on every day.
    due_date: date | None = None
    required: bool = False  # e.g. meds: must never be silently dropped
    is_completed: bool = False

    def is_due(self, day: date) -> bool:
        """True if this task should be done on `day`, based on its frequency and due date."""
        if self.due_date is None or self.frequency == Frequency.DAILY:
            return True
        if self.frequency == Frequency.ONCE:
            return self.due_date == day
        return self.due_date.weekday() == day.weekday()

    def mark_complete(self) -> None:
        """Mark the task as done."""
        self.is_completed = True

    def reset(self) -> None:
        """Clear completion, e.g. at the start of a new day for recurring tasks."""
        self.is_completed = False


@dataclass
class Pet:
    name: str
    species: str
    age: int
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and point the task back at the pet."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Raise ValueError if the task is not on this pet."""
        self.tasks.remove(task)


@dataclass
class Owner:
    name: str
    email: str
    # available_minutes_per_day: int
    pets: list[Pet] = field(default_factory=list)

    def save_info(self, path: str) -> None:
        """Write the owner, pets and tasks to a JSON file at `path`."""
        with open(path, "w") as f:
            json.dump(self._to_dict(), f, indent=2)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self, day: date) -> list[Task]:
        """Pending (not completed) tasks due on `day`, across all pets."""
        return [
            task
            for pet in self.pets
            for task in pet.tasks
            if not task.is_completed and task.is_due(day)
        ]

    def _to_dict(self) -> dict:
        """Convert the owner and everything under it into JSON-serializable data."""
        def slot(s: TimeSlot | None) -> dict | None:
            return None if s is None else {"start": s.start.isoformat(), "end": s.end.isoformat()}

        return {
            "name": self.name,
            "email": self.email,
            "pets": [
                {
                    "name": p.name,
                    "species": p.species,
                    "age": p.age,
                    "notes": p.notes,
                    "tasks": [
                        {
                            "title": t.title,
                            "type": t.type.value,
                            "duration_minutes": t.duration_minutes,
                            "priority": t.priority.name,
                            "frequency": t.frequency.value,
                            "preferred_time": slot(t.preferred_time),
                            "due_date": t.due_date.isoformat() if t.due_date else None,
                            "required": t.required,
                            "is_completed": t.is_completed,
                        }
                        for t in p.tasks
                    ],
                }
                for p in self.pets
            ],
        }


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
        """Add a scheduled task to the plan, keeping items in time order."""
        self.items.append(ScheduledItem(task, task.pet, slot, reason))
        self.items.sort(key=lambda i: i.slot.start)

    def has_missed_required(self) -> bool:
        """True if any required task ended up unscheduled."""
        return any(task.required for task in self.unscheduled)

    def total_minutes(self) -> int:
        """Total minutes of care scheduled in the plan."""
        return sum(item.slot.duration_minutes() for item in self.items)


@dataclass
class Scheduler:
    owner: Owner
    availability: list[TimeSlot] = field(default_factory=list)  # single source of free time

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order by required, then priority, then preferred time, then shorter duration."""
        return sorted(
            tasks,
            key=lambda t: (
                not t.required,
                -t.priority.value,
                t.preferred_time.start if t.preferred_time else time.max,
                t.duration_minutes,
            ),
        )

    def schedule_tasks(self, day: date) -> DailyPlan:
        """Place tasks into non-overlapping free windows; leftovers go to `unscheduled`."""
        plan = DailyPlan(day)
        free = sorted(self.availability, key=lambda s: s.start)  # copy; slots are frozen
        for task in self.prioritize_tasks(self.owner.get_all_tasks(day)):
            found = self._find_slot(free, task)
            if found is None:
                plan.unscheduled.append(task)
                continue
            slot, reason = found
            plan.add_item(task, slot, reason)
            free = self._carve(free, slot)
        return plan

    def explain_choices(self, plan: DailyPlan) -> str:
        """Join each item's `reason` and explain why tasks were left unscheduled."""
        lines = [f"Plan for {plan.date.isoformat()}:"]
        for item in plan.items:
            lines.append(
                f"- {item.slot.start:%H:%M}-{item.slot.end:%H:%M} "
                f"{item.pet.name}: {item.task.title} ({item.reason})"
            )
        for task in plan.unscheduled:
            flag = " REQUIRED task missed!" if task.required else ""
            lines.append(
                f"- Not scheduled: {task.pet.name}: {task.title} (no free window long enough).{flag}"
            )
        return "\n".join(lines)

    def _find_slot(self, free: list[TimeSlot], task: Task) -> tuple[TimeSlot, str] | None:
        """Earliest fit inside the preferred window if possible, else the first free window."""
        need = task.duration_minutes
        if task.preferred_time is not None:
            pref = task.preferred_time
            for w in free:
                lo = max(_minutes(w.start), _minutes(pref.start))
                hi = min(_minutes(w.end), _minutes(pref.end))
                if hi - lo >= need:
                    return TimeSlot(_to_time(lo), _to_time(lo + need)), self._reason(task, True)
        for w in free:
            if w.duration_minutes() >= need:
                start = _minutes(w.start)
                return TimeSlot(_to_time(start), _to_time(start + need)), self._reason(task, False)
        return None

    @staticmethod
    def _reason(task: Task, in_preferred: bool) -> str:
        """Build the short explanation for why a task was scheduled the way it was."""
        parts = []
        if task.required:
            parts.append("required")
        parts.append(f"{task.priority.name.lower()} priority")
        if task.preferred_time is not None:
            parts.append("fits preferred time" if in_preferred else "preferred time unavailable")
        return ", ".join(parts)

    @staticmethod
    def _carve(free: list[TimeSlot], used: TimeSlot) -> list[TimeSlot]:
        """Return the free windows with `used` removed, splitting a window if needed."""
        result = []
        for w in free:
            if not w.overlaps(used):
                result.append(w)
                continue
            if w.start < used.start:
                result.append(TimeSlot(w.start, used.start))
            if used.end < w.end:
                result.append(TimeSlot(used.end, w.end))
        return result
