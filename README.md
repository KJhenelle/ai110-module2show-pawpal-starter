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

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Plan for 2026-10-07:
- 08:00-08:10 Rex: Heartworm meds (required, high priority)
- 08:10-08:25 Mia: Breakfast (high priority, fits preferred time)
- 08:25-08:55 Rex: Morning walk (medium priority, fits preferred time)
- Not scheduled: Mia: Grooming (no free window long enough).
```



## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Orders tasks by preferred start time using a lambda key on `"HH:MM"` strings; tasks with no preferred time go last. |
| Plan ordering | `Scheduler.prioritize_tasks()` | Required first, then priority, then preferred time, then shorter duration. |
| Filtering | `Scheduler.filter_tasks()` | Filters by completion status (`completed=True/False`) and/or pet name (case-insensitive). Filters combine; `None` skips one. |
| Conflict detection | `Scheduler.detect_conflicts()` | Compares every pair of pending tasks' preferred times with `TimeSlot.overlaps()` and returns warning strings (same pet or different pets) instead of raising. Back-to-back tasks are not conflicts. |
| Recurring tasks | `Task.mark_complete()`, `Task.is_due()` | Completing a `DAILY` task creates a copy due `today + timedelta(days=1)`; a `WEEKLY` task's copy is due 7 days after its due date. `ONCE` tasks do not recur, and completing a task twice does not duplicate it. `is_due()` keeps a recurred copy out of today's plan. |

The scheduler itself is greedy first-fit (`Scheduler.schedule_tasks()`): if a task's preferred window is taken, it falls back to any free window, and the plan's reason text says so. See `reflection.md` section 2b for that tradeoff.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
