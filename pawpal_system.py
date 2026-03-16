from dataclasses import dataclass, field, replace
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Optional


class Frequency(Enum):
    ONE_TIME = "one_time"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Activity:
    name: str
    description: str
    start_time: time
    duration: int               # in minutes
    frequency: Frequency = Frequency.ONE_TIME
    is_complete: bool = False
    scheduled_date: Optional[date] = None   # used by ONE_TIME and WEEKLY tasks

    def end_time(self) -> time:
        """Calculate the time this activity ends based on start_time + duration."""
        total = self.start_time.hour * 60 + self.start_time.minute + self.duration
        return time(hour=(total // 60) % 24, minute=total % 60)

    def overlaps_with(self, other: "Activity") -> bool:
        """Return True if this activity's time window overlaps with another's."""
        return self.start_time < other.end_time() and other.start_time < self.end_time()

    def next_occurrence(self) -> Optional["Activity"]:
        """Return a fresh incomplete copy for the next occurrence, or None for ONE_TIME tasks."""
        if self.frequency == Frequency.ONE_TIME:
            return None
        base = self.scheduled_date or date.today()
        delta = timedelta(days=1) if self.frequency == Frequency.DAILY else timedelta(weeks=1)
        return replace(self, is_complete=False, scheduled_date=base + delta)


@dataclass
class Pet:
    name: str
    birthday: date
    type: str
    breed: str
    tasks: list[Activity] = field(default_factory=list)


@dataclass
class Owner:
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate that the owner has at least one contact method."""
        if not self.email and not self.phone:
            raise ValueError("Owner must have at least an email or a phone number.")

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[tuple["Pet", Activity]]:
        """Return every task across all pets as (pet, activity) pairs."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """The brain: retrieves, organizes, and manages tasks across an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Bind the scheduler to an owner whose pets and tasks it will manage."""
        self.owner = owner

    @staticmethod
    def _by_time(tasks: list[Activity]) -> list[Activity]:
        """Sort a list of activities by start_time."""
        return sorted(tasks, key=lambda a: a.start_time)

    # ── Retrieval ────────────────────────────────────────────────────────────

    def get_tasks(self, pet: Pet) -> list[Activity]:
        """Return all tasks for a specific pet, sorted by start time."""
        return self._by_time(pet.tasks)

    def get_all_tasks(self) -> list[tuple[Pet, Activity]]:
        """Return all tasks across every pet, sorted by start time then pet name."""
        return sorted(self.owner.get_all_tasks(), key=lambda pair: (pair[1].start_time, pair[0].name))

    def get_pending_tasks(self, pet: Pet) -> list[Activity]:
        """Return incomplete tasks for a pet, sorted by start time."""
        return self._by_time([t for t in pet.tasks if not t.is_complete])

    # ── Management ───────────────────────────────────────────────────────────

    def add_task(self, pet: Pet, activity: Activity) -> None:
        """Add a task to a pet's task list."""
        pet.tasks.append(activity)

    def remove_task(self, pet: Pet, activity: Activity) -> None:
        """Remove a task from a pet's task list."""
        pet.tasks.remove(activity)

    def edit_task(self, pet: Pet, old: Activity, new: Activity) -> None:
        """Replace an existing task with an updated version."""
        index = pet.tasks.index(old)
        pet.tasks[index] = new

    def complete_task(self, pet: Pet, activity: Activity) -> None:
        """Mark a task as complete and append the next occurrence for recurring tasks."""
        activity.is_complete = True
        next_task = activity.next_occurrence()
        if next_task is not None:
            pet.tasks.append(next_task)

    # ── Conflict Detection ───────────────────────────────────────────────────

    def get_tasks_by_frequency(self, pet: Pet, frequency: Frequency) -> list[Activity]:
        """Return tasks for a pet matching the given frequency, sorted by start time."""
        return self._by_time([t for t in pet.tasks if t.frequency == frequency])

    def get_tasks_for_pet_type(self, pet_type: str) -> list[tuple[Pet, Activity]]:
        """Return all tasks for pets of a given type (e.g. 'dog'), sorted by start time."""
        pairs = [(pet, task) for pet in self.owner.pets if pet.type == pet_type for task in pet.tasks]
        return sorted(pairs, key=lambda pair: (pair[1].start_time, pair[0].name))

    def get_tasks_for_date(self, pet: Pet, target_date: date) -> list[Activity]:
        """Return tasks that apply on target_date, respecting each task's frequency.

        - DAILY tasks are always included.
        - WEEKLY tasks are included when scheduled_date's weekday matches target_date's weekday.
        - ONE_TIME tasks are included when scheduled_date == target_date.
        """
        results = []
        for task in pet.tasks:
            if task.frequency == Frequency.DAILY:
                results.append(task)
            elif task.frequency == Frequency.WEEKLY:
                if task.scheduled_date and task.scheduled_date.weekday() == target_date.weekday():
                    results.append(task)
            else:  # ONE_TIME
                if task.scheduled_date == target_date:
                    results.append(task)
        return self._by_time(results)

    def get_upcoming_tasks(self, pet: Pet, within_minutes: int = 60) -> list[Activity]:
        """Return incomplete tasks whose start_time falls within the next within_minutes."""
        now = datetime.now()
        now_time = now.time()
        cutoff = (now + timedelta(minutes=within_minutes)).time()
        return self._by_time([
            t for t in pet.tasks
            if not t.is_complete and now_time <= t.start_time <= cutoff
        ])

    def get_overdue_tasks(self, pet: Pet) -> list[Activity]:
        """Return incomplete ONE_TIME tasks whose start_time has already passed today."""
        now = datetime.now().time()
        return self._by_time([
            t for t in pet.tasks
            if not t.is_complete and t.frequency == Frequency.ONE_TIME and t.start_time < now
        ])

    # ── Conflict Detection ───────────────────────────────────────────────────

    def detect_conflicts(self, pet: Pet) -> list[tuple[Activity, Activity]]:
        """Return pairs of overlapping activities for a pet using sort-then-scan (O(n log n))."""
        if len(pet.tasks) < 2:
            return []
        conflicts = []
        sorted_tasks = self._by_time(pet.tasks)
        for i in range(len(sorted_tasks) - 1):
            if sorted_tasks[i].overlaps_with(sorted_tasks[i + 1]):
                conflicts.append((sorted_tasks[i], sorted_tasks[i + 1]))
        return conflicts

    def detect_all_conflicts(self) -> list[tuple[Pet, Activity, Pet, Activity]]:
        """Return overlapping task pairs across all pets, sorted by start time."""
        all_pairs = sorted(self.owner.get_all_tasks(), key=lambda pair: pair[1].start_time)
        if len(all_pairs) < 2:
            return []
        conflicts = []
        for i in range(len(all_pairs) - 1):
            pet_a, task_a = all_pairs[i]
            pet_b, task_b = all_pairs[i + 1]
            if pet_a is not pet_b and task_a.overlaps_with(task_b):
                conflicts.append((pet_a, task_a, pet_b, task_b))
        return conflicts
