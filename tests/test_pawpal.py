import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, time
from pawpal_system import Activity, Frequency, Owner, Pet, Scheduler


# ── Fixtures ─────────────────────────────────────────────────────────────────

def make_activity():
    return Activity(
        name="Morning Walk",
        description="Walk around the block",
        start_time=time(8, 0),
        duration=30,
        frequency=Frequency.DAILY,
    )

def make_pet():
    return Pet(name="Fifi", birthday=date(2025, 1, 2), type="Dog", breed="Chihuahua")

def make_scheduler():
    owner = Owner(first_name="John", last_name="Doe", phone="555-555-5555")
    return Scheduler(owner)


# ── Task Completion ───────────────────────────────────────────────────────────

def test_task_is_incomplete_by_default():
    task = make_activity()
    assert task.is_complete is False

def test_complete_task_marks_task_as_done():
    task = make_activity()
    scheduler = make_scheduler()
    scheduler.complete_task(task)
    assert task.is_complete is True

def test_complete_task_does_not_affect_other_tasks():
    task_a = make_activity()
    task_b = make_activity()
    scheduler = make_scheduler()
    scheduler.complete_task(task_a)
    assert task_b.is_complete is False


# ── Task Addition ─────────────────────────────────────────────────────────────

def test_new_pet_has_no_tasks():
    pet = make_pet()
    assert len(pet.tasks) == 0

def test_add_task_increases_pet_task_count():
    pet = make_pet()
    scheduler = make_scheduler()
    scheduler.add_task(pet, make_activity())
    assert len(pet.tasks) == 1

def test_add_multiple_tasks_increases_count_correctly():
    pet = make_pet()
    scheduler = make_scheduler()
    for _ in range(3):
        scheduler.add_task(pet, make_activity())
    assert len(pet.tasks) == 3
