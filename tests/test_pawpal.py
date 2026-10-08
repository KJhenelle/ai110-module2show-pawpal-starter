from datetime import date, time, timedelta

import pytest

from pawpal_system import (
    Frequency,
    Owner,
    Pet,
    Priority,
    Scheduler,
    Task,
    TaskType,
    TimeSlot,
)

DAY = date(2026, 10, 8)


def make_task(pet, title="Morning walk", start=None, end=None, **kwargs):
    pref = TimeSlot(start, end) if start else None
    return Task(title, pet, TaskType.WALK, kwargs.pop("minutes", 30), Priority.MEDIUM,
                preferred_time=pref, **kwargs)


@pytest.fixture
def owner():
    o = Owner("Jordan", "j@example.com")
    o.add_pet(Pet("Rex", "dog", 3))
    o.add_pet(Pet("Mia", "cat", 5))
    return o


# --- Basics ---------------------------------------------------------------

def test_mark_complete_changes_status():
    pet = Pet("Rex", "dog", 3)
    task = make_task(pet)
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Rex", "dog", 3)
    assert len(pet.tasks) == 0
    pet.add_task(make_task(pet))
    assert len(pet.tasks) == 1


# --- Sorting --------------------------------------------------------------

def test_sort_by_time_is_chronological_and_untimed_last(owner):
    rex = owner.pets[0]
    for title, start in [("Evening", time(17)), ("Noon", time(12)), ("Morning", time(8))]:
        rex.add_task(make_task(rex, title, start, time(start.hour, 30)))
    rex.add_task(make_task(rex, "Anytime"))
    ordered = Scheduler(owner).sort_by_time(rex.tasks)
    assert [t.title for t in ordered] == ["Morning", "Noon", "Evening", "Anytime"]


def test_sort_handles_zero_padded_times_and_empty_list(owner):
    rex = owner.pets[0]
    rex.add_task(make_task(rex, "Late", time(10), time(10, 30)))
    rex.add_task(make_task(rex, "Early", time(9, 5), time(9, 30)))
    assert [t.title for t in Scheduler(owner).sort_by_time(rex.tasks)] == ["Early", "Late"]
    assert Scheduler(owner).sort_by_time([]) == []


# --- Filtering ------------------------------------------------------------

def test_filter_by_pet_and_status(owner):
    rex, mia = owner.pets
    done = make_task(rex, "Done")
    rex.add_task(done)
    rex.add_task(make_task(rex, "Todo"))
    mia.add_task(make_task(mia, "Mia todo"))
    done.is_completed = True
    s = Scheduler(owner)
    assert [t.title for t in s.filter_tasks(completed=True)] == ["Done"]
    assert {t.title for t in s.filter_tasks(completed=False)} == {"Todo", "Mia todo"}
    assert [t.title for t in s.filter_tasks(pet_name="MIA")] == ["Mia todo"]
    assert [t.title for t in s.filter_tasks(pet_name="rex", completed=False)] == ["Todo"]


def test_pet_with_no_tasks_is_harmless(owner):
    s = Scheduler(owner, [TimeSlot(time(8), time(9))])
    assert s.filter_tasks() == []
    assert s.detect_conflicts(DAY) == []
    plan = s.schedule_tasks(DAY)
    assert plan.items == [] and plan.unscheduled == []


# --- Recurrence -----------------------------------------------------------

def test_daily_task_recurs_tomorrow(owner):
    rex = owner.pets[0]
    task = make_task(rex, frequency=Frequency.DAILY)
    rex.add_task(task)
    new = task.mark_complete(DAY)
    assert new is not None and new is not task
    assert new.due_date == DAY + timedelta(days=1)
    assert new.is_completed is False and new.pet is rex
    assert rex.tasks == [task, new]


def test_recurred_task_not_due_until_its_date(owner):
    rex = owner.pets[0]
    task = make_task(rex)
    rex.add_task(task)
    new = task.mark_complete(DAY)
    assert not new.is_due(DAY)
    assert new.is_due(DAY + timedelta(days=1))


def test_weekly_recurs_in_seven_days_and_once_does_not(owner):
    mia = owner.pets[1]
    weekly = make_task(mia, "Groom", frequency=Frequency.WEEKLY, due_date=DAY)
    once = make_task(mia, "Vet", frequency=Frequency.ONCE)
    mia.add_task(weekly)
    mia.add_task(once)
    assert weekly.mark_complete(DAY).due_date == DAY + timedelta(days=7)
    assert once.mark_complete(DAY) is None
    assert weekly.mark_complete(DAY) is None  # already complete: no duplicate
    assert len(mia.tasks) == 3


# --- Conflicts ------------------------------------------------------------

def test_detect_conflicts_flags_overlaps_without_raising(owner):
    rex, mia = owner.pets
    at8 = (time(8), time(8, 30))
    rex.add_task(make_task(rex, "Walk", *at8))
    mia.add_task(make_task(mia, "Food", *at8))
    rex.add_task(make_task(rex, "Teeth", *at8))
    rex.add_task(make_task(rex, "Later", time(8, 30), time(9)))  # touches, no overlap
    warnings = Scheduler(owner).detect_conflicts(DAY)
    assert len(warnings) == 3
    assert sum("same pet" in w for w in warnings) == 1


def test_exact_duplicate_time_on_one_pet_is_flagged(owner):
    rex = owner.pets[0]
    rex.add_task(make_task(rex, "A", time(9), time(9, 30)))
    rex.add_task(make_task(rex, "B", time(9), time(9, 30)))
    (warning,) = Scheduler(owner).detect_conflicts(DAY)
    assert "same pet" in warning


def test_completed_tasks_do_not_conflict(owner):
    rex = owner.pets[0]
    a = make_task(rex, "A", time(9), time(9, 30))
    rex.add_task(a)
    rex.add_task(make_task(rex, "B", time(9), time(9, 30)))
    a.is_completed = True
    assert Scheduler(owner).detect_conflicts(DAY) == []


# --- Scheduling -----------------------------------------------------------

def test_schedule_never_overlaps_and_reports_leftovers(owner):
    rex = owner.pets[0]
    rex.add_task(make_task(rex, "Meds", minutes=10, required=True))
    rex.add_task(make_task(rex, "Long", minutes=120))
    plan = Scheduler(owner, [TimeSlot(time(8), time(9))]).schedule_tasks(DAY)
    assert [i.task.title for i in plan.items] == ["Meds"]
    assert [t.title for t in plan.unscheduled] == ["Long"]
    slots = [i.slot for i in plan.items]
    assert not any(a.overlaps(b) for i, a in enumerate(slots) for b in slots[i + 1:])


def test_required_task_gets_scheduled_before_optional_when_time_is_short(owner):
    rex = owner.pets[0]
    rex.add_task(Task("Play", rex, TaskType.ENRICHMENT, 30, Priority.HIGH))
    rex.add_task(Task("Meds", rex, TaskType.MEDS, 30, Priority.LOW, required=True))
    plan = Scheduler(owner, [TimeSlot(time(8), time(8, 30))]).schedule_tasks(DAY)
    assert [i.task.title for i in plan.items] == ["Meds"]
    assert plan.unscheduled[0].title == "Play"


def test_invalid_timeslot_rejected():
    with pytest.raises(ValueError):
        TimeSlot(time(9), time(8))
