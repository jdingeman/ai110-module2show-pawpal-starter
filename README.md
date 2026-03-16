# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

# TF Submission: Justin Dingeman

1. The core concept students needed to understand
   Students will need to understand how to set up a virtual environment, run a streamlit app, and be able to use AI as a collaborator for drafting all the way to app completion.

2. Where students are most likely to struggle
   The instructions almost encourage the students to hand over too much agency to the AI without discerning the changes it makes. They might struggle to keep up with it because if they are just following instructions, the AI might take it further than just the requests they make and implement changes beyond what they asked for. This makes it easy to start handing over the entire app to the AI without actually trying to understand what it's doing. The instructions also assume that the code that the AI generated would match what is written, such as the instruction that mentions editing Scheduler.sort_by_time(). There was no mention in the instructions previously that this method exists or was expected to be added, yet the instruction makes it seem like it was.

3. Where AI was helpful vs. misleading
   The AI is immensely helpful in creating tests and giving insight to the changes it makes. Mine was misleading in that it stated multiple times it fixed the issue of the schedule showing the tasks being marked as complete despite them not actually being marked as complete.

4. One way they would guide a student without giving the answer
   It depends on the question. My answer will always be to ask them to scale back to square one and determine where they started getting lost. If they can compact the entire process into a linear workflow, then they can try to identify the point in time that they started getting lost.
