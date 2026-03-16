from pawpal_system import *

owner = Owner("John", "Doe", phone="555-555-5555")
pets = [
    Pet("Fifi", date(2025, 1, 2), "Dog", "Chihuahua"),
    Pet("Whiskers", date(2024, 6, 15), "Cat", "Tabby"),
]

tasks = [
    Activity("Morning Walk",    "Take Fifi for a walk around the block",  time(8, 0),  30,  Frequency.DAILY),
    Activity("Feeding",         "Feed Whiskers her morning meal",          time(9, 0),  15,  Frequency.DAILY),
    Activity("Grooming",        "Brush Fifi's coat",                       time(17, 0), 20,  Frequency.WEEKLY),
]

for pet in pets:
    owner.add_pet(pet)

owner.pets[0].tasks.extend([tasks[0], tasks[2]])
owner.pets[1].tasks.append(tasks[2])

print("=== Today's Schedule ===\n")
for pet in owner.pets:
    print(f"  {pet.name} ({pet.type})")
    for task in pet.tasks:
        status = "✓" if task.is_complete else "○"
        print(f"    {status} {task.start_time.strftime('%I:%M %p')}  {task.name} ({task.duration} min) [{task.frequency.value}]")
    print()
