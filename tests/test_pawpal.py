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
