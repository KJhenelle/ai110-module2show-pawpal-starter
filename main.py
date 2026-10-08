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

    # Added out of time order on purpose to exercise sorting.
    mia.add_task(Task("Evening play", mia, TaskType.ENRICHMENT, 20, Priority.LOW,
                      preferred_time=TimeSlot(time(17), time(17, 30))))
    rex.add_task(Task("Lunch check-in", rex, TaskType.FEEDING, 10, Priority.MEDIUM,
                      preferred_time=TimeSlot(time(12), time(12, 30))))
    # Deliberate conflicts: Rex's flea treatment vs Mia's breakfast (different pets),
    # and Rex's teeth brushing vs his lunch check-in (same pet).
    rex.add_task(Task("Flea treatment", rex, TaskType.GROOMING, 10, Priority.MEDIUM,
                      preferred_time=TimeSlot(time(8), time(8, 30))))
    rex.add_task(Task("Brush teeth", rex, TaskType.GROOMING, 10, Priority.LOW,
                      preferred_time=TimeSlot(time(12), time(12, 30))))
    rex.tasks[0].mark_complete()  # Morning walk (daily): spawns tomorrow's copy

    scheduler = Scheduler(owner, [TimeSlot(time(8), time(9)), TimeSlot(time(17), time(17, 30))])
    plan = scheduler.schedule_tasks(date.today())
    print(scheduler.explain_choices(plan))

    print("\nConflict check:")
    for warning in scheduler.detect_conflicts(date.today()) or ["No conflicts."]:
        print(f"  {warning}")

    def show(label: str, tasks: list[Task]) -> None:
        print(f"\n{label}")
        for t in tasks:
            when = f"{t.preferred_time.start:%H:%M}" if t.preferred_time else "--:--"
            status = "done" if t.is_completed else "pending"
            print(f"  {when} {t.pet.name}: {t.title} [{status}]")

    all_tasks = scheduler.filter_tasks()
    show("Insertion order:", all_tasks)
    show("Sorted by time:", scheduler.sort_by_time(all_tasks))
    show("Pending only:", scheduler.filter_tasks(completed=False))
    show("Completed only:", scheduler.filter_tasks(completed=True))
    show("Mia's tasks:", scheduler.filter_tasks(pet_name="Mia"))
    show("Rex's pending, by time:",
         scheduler.sort_by_time(scheduler.filter_tasks(completed=False, pet_name="rex")))


if __name__ == "__main__":
    main()
