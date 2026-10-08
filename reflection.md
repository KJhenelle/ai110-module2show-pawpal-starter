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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler is greedy and first-fit: it sorts tasks by required, then priority, then preferred time, and puts each one in the first free window that fits. If a task's preferred window is already taken, it falls back to any free window instead of leaving the task unscheduled. In my demo, "Lunch check-in" (preferred 12:00) ended up at 08:35 because the owner was only free 8-9 and 17:00-17:30. The plan is not optimal: a smarter search could shuffle tasks to honor more preferences, and the fallback can put a task far from the time the owner wanted.

This is reasonable for a pet owner because a task done at the wrong time usually beats a task not done at all, and the greedy order guarantees that high-priority and required tasks (meds) get the best windows first. The reason string ("preferred time unavailable") and `detect_conflicts` warnings keep the compromise visible instead of silent. A related tradeoff: `detect_conflicts` compares every pair of preferred times with `TimeSlot.overlaps` (O(n^2)) rather than only exact start-time matches or a sorted sweep. Overlap catches real clashes like 8:00-8:30 vs 8:15-8:45, and with only a few tasks per day the simpler pairwise loop is easier to read than a faster one.

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
