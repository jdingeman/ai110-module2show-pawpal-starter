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
    pet = make_pet()
    task = make_activity()
    pet.tasks.append(task)
    scheduler = make_scheduler()
    scheduler.complete_task(pet, task)
    assert task.is_complete is True

def test_complete_task_does_not_affect_other_tasks():
    pet = make_pet()
    task_a = make_activity()
    task_b = make_activity()
    pet.tasks.extend([task_a, task_b])
    scheduler = make_scheduler()
    scheduler.complete_task(pet, task_a)
    assert task_b.is_complete is False


# ── next_occurrence / auto-scheduling ────────────────────────────────────────

def test_one_time_task_has_no_next_occurrence():
    task = Activity("Vet", "", time(10, 0), 60, Frequency.ONE_TIME)
    assert task.next_occurrence() is None

def test_daily_task_next_occurrence_is_tomorrow():
    today = date(2026, 3, 15)
    task = Activity("Walk", "", time(8, 0), 30, Frequency.DAILY, scheduled_date=today)
    nxt = task.next_occurrence()
    assert nxt is not None
    assert nxt.scheduled_date == date(2026, 3, 16)
    assert nxt.is_complete is False

def test_weekly_task_next_occurrence_is_seven_days_later():
    monday = date(2026, 3, 16)
    task = Activity("Grooming", "", time(11, 0), 45, Frequency.WEEKLY, scheduled_date=monday)
    nxt = task.next_occurrence()
    assert nxt is not None
    assert nxt.scheduled_date == date(2026, 3, 23)

def test_completing_daily_task_adds_next_occurrence_to_pet():
    pet = make_pet()
    task = Activity("Walk", "", time(8, 0), 30, Frequency.DAILY, scheduled_date=date(2026, 3, 15))
    pet.tasks.append(task)
    scheduler = make_scheduler()
    scheduler.complete_task(pet, task)
    assert len(pet.tasks) == 2
    assert pet.tasks[1].scheduled_date == date(2026, 3, 16)
    assert pet.tasks[1].is_complete is False

def test_completing_weekly_task_adds_next_occurrence_to_pet():
    pet = make_pet()
    task = Activity("Bath", "", time(10, 0), 30, Frequency.WEEKLY, scheduled_date=date(2026, 3, 16))
    pet.tasks.append(task)
    scheduler = make_scheduler()
    scheduler.complete_task(pet, task)
    assert len(pet.tasks) == 2
    assert pet.tasks[1].scheduled_date == date(2026, 3, 23)

def test_completing_one_time_task_does_not_add_new_task():
    pet = make_pet()
    task = Activity("Vet", "", time(9, 0), 60, Frequency.ONE_TIME)
    pet.tasks.append(task)
    scheduler = make_scheduler()
    scheduler.complete_task(pet, task)
    assert len(pet.tasks) == 1

def test_next_occurrence_inherits_same_name_and_duration():
    task = Activity("Evening walk", "", time(18, 0), 45, Frequency.DAILY, scheduled_date=date(2026, 3, 15))
    nxt = task.next_occurrence()
    assert nxt is not None
    assert nxt.name == task.name
    assert nxt.duration == task.duration
    assert nxt.start_time == task.start_time

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


# ── get_tasks_by_frequency ────────────────────────────────────────────────────

def test_filter_by_frequency_returns_matching_tasks():
    pet = make_pet()
    scheduler = make_scheduler()
    daily = Activity("Walk", "", time(8, 0), 30, Frequency.DAILY)
    one_time = Activity("Vet", "", time(9, 0), 60, Frequency.ONE_TIME)
    scheduler.add_task(pet, daily)
    scheduler.add_task(pet, one_time)
    result = scheduler.get_tasks_by_frequency(pet, Frequency.DAILY)
    assert result == [daily]

def test_filter_by_frequency_empty_when_none_match():
    pet = make_pet()
    scheduler = make_scheduler()
    scheduler.add_task(pet, Activity("Walk", "", time(8, 0), 30, Frequency.DAILY))
    result = scheduler.get_tasks_by_frequency(pet, Frequency.WEEKLY)
    assert result == []

def test_filter_by_frequency_sorted_by_start_time():
    pet = make_pet()
    scheduler = make_scheduler()
    late = Activity("Evening walk", "", time(18, 0), 30, Frequency.DAILY)
    early = Activity("Morning walk", "", time(7, 0), 30, Frequency.DAILY)
    scheduler.add_task(pet, late)
    scheduler.add_task(pet, early)
    result = scheduler.get_tasks_by_frequency(pet, Frequency.DAILY)
    assert result == [early, late]


# ── get_tasks_for_pet_type ────────────────────────────────────────────────────

def test_filter_by_pet_type_returns_only_matching():
    owner = Owner(first_name="Jane", last_name="Doe", phone="555-000-0000")
    dog = Pet(name="Rex", birthday=date(2022, 1, 1), type="dog", breed="Lab")
    cat = Pet(name="Whiskers", birthday=date(2021, 6, 1), type="cat", breed="Tabby")
    dog_task = Activity("Walk", "", time(8, 0), 30, Frequency.DAILY)
    cat_task = Activity("Feed", "", time(9, 0), 10, Frequency.DAILY)
    dog.tasks.append(dog_task)
    cat.tasks.append(cat_task)
    owner.add_pet(dog)
    owner.add_pet(cat)
    scheduler = Scheduler(owner)
    result = scheduler.get_tasks_for_pet_type("dog")
    assert len(result) == 1
    assert result[0] == (dog, dog_task)

def test_filter_by_pet_type_empty_when_no_match():
    owner = Owner(first_name="Jane", last_name="Doe", phone="555-000-0000")
    owner.add_pet(Pet(name="Rex", birthday=date(2022, 1, 1), type="dog", breed="Lab"))
    scheduler = Scheduler(owner)
    assert scheduler.get_tasks_for_pet_type("bird") == []


# ── get_tasks_for_date ────────────────────────────────────────────────────────

def test_daily_task_included_on_any_date():
    pet = make_pet()
    scheduler = make_scheduler()
    task = Activity("Walk", "", time(8, 0), 30, Frequency.DAILY)
    scheduler.add_task(pet, task)
    assert task in scheduler.get_tasks_for_date(pet, date(2026, 1, 1))
    assert task in scheduler.get_tasks_for_date(pet, date(2026, 6, 15))

def test_one_time_task_only_on_matching_date():
    pet = make_pet()
    scheduler = make_scheduler()
    target = date(2026, 5, 10)
    task = Activity("Vet", "", time(10, 0), 60, Frequency.ONE_TIME, scheduled_date=target)
    scheduler.add_task(pet, task)
    assert task in scheduler.get_tasks_for_date(pet, target)
    assert task not in scheduler.get_tasks_for_date(pet, date(2026, 5, 11))

def test_weekly_task_on_matching_weekday():
    pet = make_pet()
    scheduler = make_scheduler()
    monday = date(2026, 3, 16)  # a Monday
    task = Activity("Grooming", "", time(11, 0), 45, Frequency.WEEKLY, scheduled_date=monday)
    scheduler.add_task(pet, task)
    next_monday = date(2026, 3, 23)
    assert task in scheduler.get_tasks_for_date(pet, next_monday)
    tuesday = date(2026, 3, 17)
    assert task not in scheduler.get_tasks_for_date(pet, tuesday)


# ── detect_conflicts (optimised) ──────────────────────────────────────────────

def test_no_conflicts_when_tasks_do_not_overlap():
    pet = make_pet()
    scheduler = make_scheduler()
    a = Activity("Walk", "", time(8, 0), 30, Frequency.DAILY)
    b = Activity("Feed", "", time(9, 0), 15, Frequency.DAILY)
    scheduler.add_task(pet, a)
    scheduler.add_task(pet, b)
    assert scheduler.detect_conflicts(pet) == []

def test_conflict_detected_for_overlapping_tasks():
    pet = make_pet()
    scheduler = make_scheduler()
    a = Activity("Walk", "", time(8, 0), 60, Frequency.DAILY)
    b = Activity("Bath", "", time(8, 30), 30, Frequency.DAILY)
    scheduler.add_task(pet, a)
    scheduler.add_task(pet, b)
    assert len(scheduler.detect_conflicts(pet)) == 1

def test_no_conflicts_for_empty_task_list():
    pet = make_pet()
    scheduler = make_scheduler()
    assert scheduler.detect_conflicts(pet) == []


# ── detect_all_conflicts ──────────────────────────────────────────────────────

def test_cross_pet_conflict_detected():
    owner = Owner(first_name="Sam", last_name="Smith", phone="555-111-2222")
    dog = Pet(name="Buddy", birthday=date(2021, 1, 1), type="dog", breed="Poodle")
    cat = Pet(name="Luna", birthday=date(2020, 3, 5), type="cat", breed="Persian")
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.tasks.append(Activity("Walk", "", time(8, 0), 60, Frequency.DAILY))
    cat.tasks.append(Activity("Feed", "", time(8, 30), 15, Frequency.DAILY))
    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_all_conflicts()
    assert len(conflicts) == 1

def test_no_cross_pet_conflict_when_tasks_are_sequential():
    owner = Owner(first_name="Sam", last_name="Smith", phone="555-111-2222")
    dog = Pet(name="Buddy", birthday=date(2021, 1, 1), type="dog", breed="Poodle")
    cat = Pet(name="Luna", birthday=date(2020, 3, 5), type="cat", breed="Persian")
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.tasks.append(Activity("Walk", "", time(8, 0), 30, Frequency.DAILY))
    cat.tasks.append(Activity("Feed", "", time(9, 0), 15, Frequency.DAILY))
    scheduler = Scheduler(owner)
    assert scheduler.detect_all_conflicts() == []
