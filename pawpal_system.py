from dataclasses import dataclass, field
from datetime import date, time, timedelta
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

    def end_time(self) -> time:
        """Calculate the time this activity ends based on start_time + duration."""
        start_delta = timedelta(hours=self.start_time.hour, minutes=self.start_time.minute)
        end_delta = start_delta + timedelta(minutes=self.duration)
        total_minutes = int(end_delta.total_seconds() // 60)
        return time(hour=(total_minutes // 60) % 24, minute=total_minutes % 60)

    def overlaps_with(self, other: "Activity") -> bool:
        """Return True if this activity's time window overlaps with another's."""
        return self.start_time < other.end_time() and other.start_time < self.end_time()


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

    # ── Retrieval ────────────────────────────────────────────────────────────

    def get_tasks(self, pet: Pet) -> list[Activity]:
        """Return all tasks for a specific pet, sorted by start time."""
        return sorted(pet.tasks, key=lambda a: a.start_time)

    def get_all_tasks(self) -> list[tuple[Pet, Activity]]:
        """Return all tasks across every pet, sorted by start time."""
        return sorted(self.owner.get_all_tasks(), key=lambda pair: pair[1].start_time)

    def get_pending_tasks(self, pet: Pet) -> list[Activity]:
        """Return incomplete tasks for a pet, sorted by start time."""
        return sorted(
            [t for t in pet.tasks if not t.is_complete],
            key=lambda a: a.start_time,
        )

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

    def complete_task(self, activity: Activity) -> None:
        """Mark a task as complete."""
        activity.is_complete = True

    # ── Conflict Detection ───────────────────────────────────────────────────

    def detect_conflicts(self, pet: Pet) -> list[tuple[Activity, Activity]]:
        """Return pairs of activities whose time windows overlap for a given pet."""
        conflicts = []
        tasks = pet.tasks
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                if tasks[i].overlaps_with(tasks[j]):
                    conflicts.append((tasks[i], tasks[j]))
        return conflicts
