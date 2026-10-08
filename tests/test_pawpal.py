from pawpal_system import Pet, Priority, Task, TaskType


def make_task(pet):
    return Task("Morning walk", pet, TaskType.WALK, 30, Priority.MEDIUM)


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


def test_daily_task_recurs_tomorrow():
    from datetime import date, timedelta
    from pawpal_system import Frequency, Pet, Priority, Task, TaskType

    pet = Pet("Rex", "dog", 3)
    task = Task("Walk", pet, TaskType.WALK, 30, Priority.MEDIUM, frequency=Frequency.DAILY)
    pet.add_task(task)
    today = date(2026, 10, 8)
    new = task.mark_complete(today)
    assert new is not None and new is not task
    assert new.due_date == today + timedelta(days=1)
    assert new.is_completed is False and new.pet is pet
    assert pet.tasks == [task, new]


def test_weekly_task_recurs_in_seven_days_and_once_does_not():
    from datetime import date, timedelta
    from pawpal_system import Frequency, Pet, Priority, Task, TaskType

    pet = Pet("Mia", "cat", 5)
    due = date(2026, 10, 8)
    weekly = Task("Groom", pet, TaskType.GROOMING, 60, Priority.LOW,
                  frequency=Frequency.WEEKLY, due_date=due)
    once = Task("Vet", pet, TaskType.MEDS, 30, Priority.HIGH, frequency=Frequency.ONCE)
    pet.add_task(weekly)
    pet.add_task(once)
    assert weekly.mark_complete(due).due_date == due + timedelta(days=7)
    assert once.mark_complete(due) is None
    assert weekly.mark_complete(due) is None  # already complete: no duplicate
    assert len(pet.tasks) == 3


def test_detect_conflicts_flags_overlaps_without_raising():
    from datetime import date, time
    from pawpal_system import Owner, Pet, Priority, Scheduler, Task, TaskType, TimeSlot

    owner = Owner("J", "j@example.com")
    rex, mia = Pet("Rex", "dog", 3), Pet("Mia", "cat", 5)
    owner.add_pet(rex)
    owner.add_pet(mia)
    at8 = TimeSlot(time(8), time(8, 30))
    rex.add_task(Task("Walk", rex, TaskType.WALK, 20, Priority.LOW, preferred_time=at8))
    mia.add_task(Task("Food", mia, TaskType.FEEDING, 10, Priority.HIGH, preferred_time=at8))
    rex.add_task(Task("Teeth", rex, TaskType.GROOMING, 10, Priority.LOW, preferred_time=at8))
    rex.add_task(Task("Later", rex, TaskType.WALK, 10, Priority.LOW,
                      preferred_time=TimeSlot(time(8, 30), time(9))))  # touches, no overlap
    warnings = Scheduler(owner, []).detect_conflicts(date(2026, 10, 8))
    assert len(warnings) == 3
    assert sum("same pet" in w for w in warnings) == 1
