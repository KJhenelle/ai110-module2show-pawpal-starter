# PawPal+ Project Reflection

## 1. System Design
The App should:
 - Enter basic owner + pet info
 - Track pet care tasks ie walks, feeding, meds, enrichment, grooming
 - Generate a daily schedule/plan
 - Explain why it chose that plan
Attributes:
 - pet info
 - owner info
 - time info
Methods
 - schedule pet care task
 - explain scheduling choices
 - store user info
 - prioritize important tasks

**a. Initial design**

Initial UML design:
The scheduler plans for the owner and creates a daily plan using the time availibility. The Owner class owns a a pet which has a task that is contained in the daily plan That task is one of three priorities and task types and it has a prefered time which is placed in the time slot. 

Classes included:
Owner 
Pet
Task 
TimeSlot
Scheduler
DailyPlan
ScheduledItem
TaskType
Priority 
    



**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.


 - PetTask = tuple[Pet, Task] now links a task to its pet. Owner.get_all_tasks(day) returns these pairs, and DailyPlan.unscheduled holds them too.
 -  I removed Owner.available_minutes_per_day. Scheduler.availability is now the only record of free time.
 - Task.due_date is new, and None means the task recurs daily. Task.is_due(day) is a new stub. schedule_tasks(day) takes a day, and get_all_tasks(day) only returns pending tasks due that day.
 -  Owner.save_info(path) now takes a path to save to.
 -  DailyPlan.add_item now takes the pet.
 - Rename: I renamed DailyPlan.date to day, because the field name was shadowing the date type.
 - Time slots: TimeSlot is frozen and rejects an end time that isn't after the start.
 - Required tasks: Task.required marks tasks like meds that can't be dropped. DailyPlan.has_missed_required() is a new stub that reports when one was.
 - Ordering and explanation: The docstrings say prioritize_tasks orders by required, then priority, then preferred time, then shorter duration. They say explain_choices joins each item's reason and explains why tasks were left out.
 - Completed tasks: completed tasks are skipped through get_all_tasks.
 - Pet age: Pet.age is now age_months.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers four constraints: the owner's free time windows, whether a task is required (like meds), task priority, and each task's preferred time and duration. I ranked them in that order: a required task that is dropped is a real harm to the pet, priority decides which of the remaining tasks matter most, and a preferred time is a nice-to-have that the scheduler will give up (and say so) when the window is taken. Duration is the final tie-breaker, so short tasks fit into leftover gaps.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler is greedy and first-fit: it sorts tasks by required, then priority, then preferred time, and puts each one in the first free window that fits. If a task's preferred window is already taken, it falls back to any free window instead of leaving the task unscheduled. In my demo, "Lunch check-in" (preferred 12:00) ended up at 08:35 because the owner was only free 8-9 and 17:00-17:30. The plan is not optimal: a smarter search could shuffle tasks to honor more preferences, and the fallback can put a task far from the time the owner wanted.

This is reasonable for a pet owner because a task done at the wrong time usually beats a task not done at all, and the greedy order guarantees that high-priority and required tasks (meds) get the best windows first. The reason string ("preferred time unavailable") and `detect_conflicts` warnings keep the compromise visible instead of silent. A related tradeoff: `detect_conflicts` compares every pair of preferred times with `TimeSlot.overlaps` (O(n^2)) rather than only exact start-time matches or a sorted sweep. Overlap catches real clashes like 8:00-8:30 vs 8:15-8:45, and with only a few tasks per day the simpler pairwise loop is easier to read than a faster one.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code for UML brainstorming, generating the class skeleton, implementing the scheduler, drafting tests, and reviewing my skeleton for missing relationships. The most useful prompts were specific and tied to my files, for example "how should the Scheduler retrieve all tasks from the Owner's pets?" and "what edge cases matter for sorting and recurring tasks?". Broad prompts like "make it smarter" gave generic results.

**b. Judgment and verification**

One example is conflict detection. The simplest suggestion is to flag only tasks with exactly the same start time, but that misses real clashes like 8:00-8:30 against 8:15-8:45, so I kept an overlap check built on `TimeSlot.overlaps`. I also kept the readable `sort_by_time` key on "HH:MM" strings instead of a terser one-liner. I verified suggestions by running `main.py` with deliberate conflicts and out-of-order tasks, and by writing tests that pin down the edge cases (back-to-back tasks are not conflicts, completing a task twice does not duplicate it).

---

## 4. Testing and Verification

**a. What you tested**

I tested sorting (including tasks with no time), filtering by pet and status, daily/weekly/once recurrence, conflict detection (same pet, different pets, exact duplicates, back-to-back, completed tasks), and scheduling edge cases (a pet with no tasks, no overlapping slots, required tasks winning scarce time, leftovers reported). These are the behaviors the owner relies on: a wrong sort order or a silently missed medication would make the plan untrustworthy.

**b. Confidence**

About 4 out of 5. All 15 tests pass and the algorithms are covered, but the Streamlit UI was only smoke-tested. Next I would test tasks that cross midnight, tasks longer than any free window, many tasks competing for one window, and weekly tasks completed on a different weekday than their due date.

---

## 5. Reflection

**a. What went well**

I am most satisfied with the separation between the logic layer (`pawpal_system.py`) and the UI. Because the scheduler works from the terminal first, the Streamlit app only had to call existing methods, and the plan explains its own choices.

**b. What you would improve**

I would let the scheduler move conflicting tasks to a nearby time instead of only warning, support tasks that overlap by duration after being rescheduled, and persist data (`Owner.save_info` writes JSON but nothing loads it back yet).

**c. Key takeaway**

AI can produce a lot of working code quickly, so the human job shifts to being the lead architect: deciding what the classes are, what each one is responsible for, and which tradeoffs are acceptable. My design changed several times (adding `Frequency`, giving `Task` a back-reference to its `Pet`, removing `available_minutes_per_day`), and each change was a decision I had to make and then verify with tests rather than trust.

**AI strategy notes**

- *Most effective features:* agent-style multi-file edits (changing `Task`, `Scheduler` and `main.py` together for recurrence) and asking the assistant to review my skeleton against my UML.
- *Rejected/modified suggestion:* see 3b above, where I kept overlap-based conflict detection and the readable sort key.
- *Separate chat sessions per phase:* I kept design, implementation, algorithms and testing as separate conversations so each had focused context and I could compare what each one proposed.
