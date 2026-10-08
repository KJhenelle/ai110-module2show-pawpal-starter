from datetime import date, time

from pawpal_system import (
    DailyPlan,
    Frequency,
    Owner,
    Pet,
    Priority,
    ScheduledItem,
    Scheduler,
    Task,
    TaskType,
    TimeSlot,
)


def main() -> None:
    owner = Owner("Jordan", "jordan@example.com")
    rex = Pet("Rex", "dog", 3)
    mia = Pet("Mia", "cat", 5)
    owner.add_pet(rex)
    owner.add_pet(mia)

    rex.add_task(Task("Morning walk", rex, TaskType.WALK, 30, Priority.MEDIUM,
                      preferred_time=TimeSlot(time(8), time(9))))
    rex.add_task(Task("Heartworm meds", rex, TaskType.MEDS, 10, Priority.HIGH, required=True))
    mia.add_task(Task("Breakfast", mia, TaskType.FEEDING, 15, Priority.HIGH,
                      preferred_time=TimeSlot(time(8), time(8, 30))))
    mia.add_task(Task("Grooming", mia, TaskType.GROOMING, 60, Priority.LOW,
                      frequency=Frequency.WEEKLY, due_date=date.today()))

    scheduler = Scheduler(owner, [TimeSlot(time(8), time(9)), TimeSlot(time(17), time(17, 30))])
    plan = scheduler.schedule_tasks(date.today())
    print(scheduler.explain_choices(plan))


if __name__ == "__main__":
    main()
