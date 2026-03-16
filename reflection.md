# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Three core actions that a user should be able to perform are:

1. Add a pet profile to store information on their pet
2. Request a daily plan of activties for their pet
3. Be able to edit tasks and activities as needed to match their pets needs.

Classes needed for this application are the owner, a pet, an activity, and a schedule.
An owner should have a first name, last name, and an email or a phone number. An owner (the user) can set up their profile and their pet(s) profile(s), edit tasks and schedules.
A pet should have a name, a birthday, a type, and a breed. An owner can have multiple pets.
An activity should have a name/description and a duration.
A schedule should be able to hold several activities and detect scheduling conflicts.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Several changes were applied:

1. Date was added to Schedule so that schedules can be distinguished between days, such as if Monday's schedule is different from Tuesday's.
2. `detect_conflicts()` in Schedule was updated so that it returns tuples of activties that conflict with each other, rather than just a list of activities that have _some_ conflict with others.
3. `start_time` was added to Activity since `duration` alone does not provide sufficient information for the schedule
4. `schedule` was added to Pet so that a pet has its own schedule, otherwise there was no relationship.
5. `__post_init__()` was added to Owner so that either a phone number or email must be provided, otherwise, it would've accepted neither being added.
6. A to-do stub was added to `setup_pet_profile()` in Owner to ensure the function adds the Pet to the Owner and link them
7. `edit_schedule()` in Owner was changed so that the schedule is linked with the pet, otherwise the attribute is ambiguous.

Beginning Phase 1 changes:

1. Enum of Frequency was added
2. `frequency` and `is_complete` added to Activity
3. `end_time()` added to Activity to calculate the end time based on `duration` and `start_time`
4. `overlaps_with(other)` added to check whether an activity conflicts with the `other` activity passed in
5. `tasks` replaced `schedule` in Pet since the Schedule class becomes Scheduler and acts as a service rather than a dataclass
6. Removed task-management methods from Owner since they will be handled by Scheduler
7. Replaced Schedule with Scheduler and added task-management methods for retrieval, editing and conflict detection

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
