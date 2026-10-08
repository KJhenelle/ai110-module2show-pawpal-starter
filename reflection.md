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
