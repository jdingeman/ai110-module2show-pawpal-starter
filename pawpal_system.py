from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Activity:
    name: str
    description: str
    duration: int  # in minutes


@dataclass
class Schedule:
    activities: list[Activity] = field(default_factory=list)

    def add_activity(self, activity: Activity) -> None:
        pass

    def detect_conflicts(self) -> list[Activity]:
        raise NotImplementedError


@dataclass
class Pet:
    name: str
    birthday: date
    type: str
    breed: str
    schedule: Schedule = field(default_factory=Schedule)


@dataclass
class Owner:
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    pets: list[Pet] = field(default_factory=list)

    def setup_profile(self) -> None:
        pass

    def setup_pet_profile(self) -> Pet:
        raise NotImplementedError

    def edit_task(self, schedule: Schedule, old: Activity, new: Activity) -> None:
        pass

    def edit_schedule(self, pet: Pet, schedule: Schedule) -> None:
        pass
