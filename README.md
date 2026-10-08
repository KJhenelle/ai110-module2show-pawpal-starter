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

## ✨ Features

- **Daily plan generation:** `Scheduler.schedule_tasks()` places tasks greedily into the owner's free windows, with a plain-English reason for each choice (`explain_choices()`).
- **Priority ordering:** `prioritize_tasks()` orders by required, then priority, then preferred time, then shorter duration, so meds never lose a window to a play session.
- **Sorting by time:** `sort_by_time()` orders tasks chronologically by preferred start; tasks without a time go last.
- **Filtering:** `filter_tasks()` narrows by pet name and/or completion status.
- **Conflict warnings:** `detect_conflicts()` returns warning messages for overlapping preferred times, for the same pet or different pets. It never raises.
- **Daily/weekly recurrence:** completing a recurring task with `Task.mark_complete()` queues the next occurrence (`today + 1 day`, or the due date + 7 days).
- **Streamlit UI:** add pets, tasks and free windows; filter and sort the task table; mark tasks complete; generate the plan with conflict warnings and unscheduled-task alerts.

## 🖥️ Sample Output

Output of `python main.py`:

```
Plan for 2026-10-08:
- 08:00-08:10 Rex: Heartworm meds (required, high priority)
- 08:10-08:25 Mia: Breakfast (high priority, fits preferred time)
- 08:25-08:35 Rex: Flea treatment (medium priority, preferred time unavailable)
- 08:35-08:45 Rex: Lunch check-in (medium priority, preferred time unavailable)
- 08:45-08:55 Rex: Brush teeth (low priority, preferred time unavailable)
- 17:00-17:20 Mia: Evening play (low priority, fits preferred time)
- Not scheduled: Mia: Grooming (no free window long enough).

Conflict check:
  WARNING (different pets): Rex: Flea treatment (08:00-08:30) overlaps Mia: Breakfast (08:00-08:30)
  WARNING (same pet): Rex: Lunch check-in (12:00-12:30) overlaps Rex: Brush teeth (12:00-12:30)

Insertion order:
  08:00 Rex: Morning walk [done]
  --:-- Rex: Heartworm meds [pending]
  12:00 Rex: Lunch check-in [pending]
  08:00 Rex: Flea treatment [pending]
  12:00 Rex: Brush teeth [pending]
  08:00 Rex: Morning walk [pending]
  08:00 Mia: Breakfast [pending]
  --:-- Mia: Grooming [pending]
  17:00 Mia: Evening play [pending]

Sorted by time:
  08:00 Rex: Morning walk [done]
  08:00 Rex: Flea treatment [pending]
  08:00 Rex: Morning walk [pending]
  08:00 Mia: Breakfast [pending]
  12:00 Rex: Lunch check-in [pending]
  12:00 Rex: Brush teeth [pending]
  17:00 Mia: Evening play [pending]
  --:-- Rex: Heartworm meds [pending]
  --:-- Mia: Grooming [pending]

Pending only:
  --:-- Rex: Heartworm meds [pending]
  12:00 Rex: Lunch check-in [pending]
  08:00 Rex: Flea treatment [pending]
  12:00 Rex: Brush teeth [pending]
  08:00 Rex: Morning walk [pending]
  08:00 Mia: Breakfast [pending]
  --:-- Mia: Grooming [pending]
  17:00 Mia: Evening play [pending]

Completed only:
  08:00 Rex: Morning walk [done]

Mia's tasks:
  08:00 Mia: Breakfast [pending]
  --:-- Mia: Grooming [pending]
  17:00 Mia: Evening play [pending]

Rex's pending, by time:
  08:00 Rex: Flea treatment [pending]
  08:00 Rex: Morning walk [pending]
  12:00 Rex: Lunch check-in [pending]
  12:00 Rex: Brush teeth [pending]
  --:-- Rex: Heartworm meds [pending]
```

## 🧪 Testing PawPal+

```bash
python -m pytest
```

The suite in `tests/test_pawpal.py` (15 tests) covers:

- **Basics:** `mark_complete()` flips status; adding a task grows the pet's list.
- **Sorting:** chronological order, tasks with no time last, zero-padded times, empty list.
- **Filtering:** by pet (case-insensitive), by status, and both together.
- **Recurrence:** daily creates a copy due tomorrow, weekly +7 days, `ONCE` and already-completed tasks create nothing, and a recurred copy isn't due early.
- **Conflicts:** same-pet and different-pet overlaps, exact duplicate times, back-to-back tasks are not conflicts, completed tasks are ignored.
- **Scheduling edge cases:** a pet with no tasks, no overlapping slots in a plan, required tasks win scarce time, leftovers are reported, invalid `TimeSlot` is rejected.

Test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.12.2, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/jhenelle/Documents/GitHub/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 15 items

tests/test_pawpal.py ...............                                     [100%]

============================== 15 passed in 0.02s ==============================
```

**Confidence level: ★★★★☆ (4/5).** Core logic (sorting, recurrence, conflicts, plan building) is well covered and passes. Not covered: the Streamlit UI (only smoke-tested by hand), tasks that span midnight, and overlapping durations once the scheduler moves a task off its preferred time.

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

**Main UI features** (run with `streamlit run app.py`): four tabs.

- **Owner & Pets:** save owner details and add pets (name, species, age, notes).
- **Tasks:** add tasks (type, duration, priority, frequency, optional preferred time, required flag). A table lists them sorted by time, with filters for pet and status, and a "Mark complete" control.
- **Availability:** add the free windows you have for pet care.
- **Today's Plan:** pick a day and generate the schedule.

**Example workflow:** add pets Rex and Mia → add "Flea treatment" (Rex) and "Breakfast" (Mia), both preferring 08:00-08:30 → add an 08:00-09:00 availability window → generate the plan.

**Scheduler behaviors you will see:**

1. **Sorting:** the task table is ordered by preferred start time.
2. **Filtering:** the pet and status dropdowns narrow the table.
3. **Conflict warnings:** a yellow warning names both overlapping tasks (same pet or different pets).
4. **Reasoned plan:** each slot shows why it was chosen; tasks that don't fit appear as warnings, and a missed required task shows as an error.
5. **Recurrence:** marking a daily or weekly task complete shows when the next copy is due.

**Sample CLI output** from `python main.py`:

```
Plan for 2026-10-08:
- 08:00-08:10 Rex: Heartworm meds (required, high priority)
- 08:10-08:25 Mia: Breakfast (high priority, fits preferred time)
- 08:25-08:35 Rex: Flea treatment (medium priority, preferred time unavailable)
- 08:35-08:45 Rex: Lunch check-in (medium priority, preferred time unavailable)
- 08:45-08:55 Rex: Brush teeth (low priority, preferred time unavailable)
- 17:00-17:20 Mia: Evening play (low priority, fits preferred time)
- Not scheduled: Mia: Grooming (no free window long enough).

Conflict check:
  WARNING (different pets): Rex: Flea treatment (08:00-08:30) overlaps Mia: Breakfast (08:00-08:30)
  WARNING (same pet): Rex: Lunch check-in (12:00-12:30) overlaps Rex: Brush teeth (12:00-12:30)

Insertion order:
  08:00 Rex: Morning walk [done]
  --:-- Rex: Heartworm meds [pending]
  12:00 Rex: Lunch check-in [pending]
  08:00 Rex: Flea treatment [pending]
  12:00 Rex: Brush teeth [pending]
  08:00 Rex: Morning walk [pending]
  08:00 Mia: Breakfast [pending]
  --:-- Mia: Grooming [pending]
  17:00 Mia: Evening play [pending]

Sorted by time:
  08:00 Rex: Morning walk [done]
  08:00 Rex: Flea treatment [pending]
  08:00 Rex: Morning walk [pending]
  08:00 Mia: Breakfast [pending]
  12:00 Rex: Lunch check-in [pending]
  12:00 Rex: Brush teeth [pending]
  17:00 Mia: Evening play [pending]
  --:-- Rex: Heartworm meds [pending]
  --:-- Mia: Grooming [pending]

Pending only:
  --:-- Rex: Heartworm meds [pending]
  12:00 Rex: Lunch check-in [pending]
  08:00 Rex: Flea treatment [pending]
  12:00 Rex: Brush teeth [pending]
  08:00 Rex: Morning walk [pending]
  08:00 Mia: Breakfast [pending]
  --:-- Mia: Grooming [pending]
  17:00 Mia: Evening play [pending]

Completed only:
  08:00 Rex: Morning walk [done]

Mia's tasks:
  08:00 Mia: Breakfast [pending]
  --:-- Mia: Grooming [pending]
  17:00 Mia: Evening play [pending]

Rex's pending, by time:
  08:00 Rex: Flea treatment [pending]
  08:00 Rex: Morning walk [pending]
  12:00 Rex: Lunch check-in [pending]
  12:00 Rex: Brush teeth [pending]
  --:-- Rex: Heartworm meds [pending]
```
