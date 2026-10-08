from datetime import date, time
from html import escape

import streamlit as st

from pawpal_system import (
    Frequency,
    Owner,
    Pet,
    Priority,
    Scheduler,
    Task,
    TaskType,
    TimeSlot,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

SPECIES_EMOJI = {"dog": "🐶", "cat": "🐱", "other": "🐾"}
TYPE_EMOJI = {
    TaskType.WALK: "🦮",
    TaskType.FEEDING: "🍖",
    TaskType.MEDS: "💊",
    TaskType.ENRICHMENT: "🧸",
    TaskType.GROOMING: "🛁",
}
PRIORITY_COLOR = {Priority.HIGH: "#e5484d", Priority.MEDIUM: "#f5a524", Priority.LOW: "#30a46c"}

st.markdown(
    """
<style>
.block-container { padding-top: 2rem; max-width: 760px; }
.hero {
    background: linear-gradient(135deg, #ff9966 0%, #ff5e62 100%);
    color: white; padding: 1.6rem 1.8rem; border-radius: 18px; margin-bottom: 1.2rem;
}
.hero h1 { margin: 0; font-size: 2.2rem; color: white; }
.hero p { margin: .3rem 0 0; opacity: .92; }
.card {
    border: 1px solid rgba(128,128,128,.25); border-radius: 14px;
    padding: .8rem 1rem; margin-bottom: .6rem; background: rgba(128,128,128,.06);
}
.card .title { font-weight: 600; font-size: 1.02rem; }
.card .meta { opacity: .75; font-size: .88rem; }
.badge {
    display: inline-block; padding: .08rem .55rem; border-radius: 999px;
    font-size: .75rem; font-weight: 600; color: white; margin-left: .4rem;
}
.slot {
    border-left: 5px solid #ff5e62; border-radius: 10px; padding: .7rem 1rem;
    margin-bottom: .6rem; background: rgba(255,94,98,.07);
}
.slot .time { font-weight: 700; font-variant-numeric: tabular-nums; }
.slot .why { opacity: .75; font-size: .86rem; }
div[data-testid="stMetric"] {
    background: rgba(128,128,128,.07); border-radius: 14px; padding: .6rem .9rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# Streamlit reruns this script on every interaction, so anything that must survive
# lives in st.session_state. Only create the objects the first time through.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", "")
if "availability" not in st.session_state:
    st.session_state.availability = [TimeSlot(time(8), time(10))]

owner: Owner = st.session_state.owner
all_tasks = [t for p in owner.pets for t in p.tasks]


def badge(priority: Priority) -> str:
    return f'<span class="badge" style="background:{PRIORITY_COLOR[priority]}">{priority.name.title()}</span>'


st.markdown(
    f"""
<div class="hero">
  <h1>🐾 PawPal+</h1>
  <p>Hi {escape(owner.name or "there")}! Plan a happy, well-cared-for day for every pet.</p>
</div>
""",
    unsafe_allow_html=True,
)

m1, m2, m3 = st.columns(3)
m1.metric("🐾 Pets", len(owner.pets))
m2.metric("📋 Tasks", len(all_tasks))
m3.metric("⏰ Free windows", len(st.session_state.availability))

tab_pets, tab_tasks, tab_time, tab_plan = st.tabs(
    ["🐕 Owner & Pets", "📋 Tasks", "⏰ Availability", "📅 Today's Plan"]
)

# --- Owner & pets ----------------------------------------------------------
with tab_pets:
    with st.expander("👤 Owner details", expanded=not owner.email):
        with st.form("owner_form"):
            name = st.text_input("Owner name", value=owner.name)
            email = st.text_input("Email", value=owner.email)
            if st.form_submit_button("Save owner", use_container_width=True):
                owner.name, owner.email = name, email
                st.success("Owner saved.")

    st.markdown("#### Add a pet")
    with st.form("pet_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        pet_name = c1.text_input("Pet name")
        species = c2.selectbox("Species", ["dog", "cat", "other"])
        age = c3.number_input("Age (years)", min_value=0, max_value=40, value=1)
        notes = st.text_input("Notes (optional)", placeholder="Allergies, quirks, favorite toy...")
        if st.form_submit_button("Add pet", type="primary", use_container_width=True):
            if pet_name.strip():
                owner.add_pet(Pet(pet_name.strip(), species, int(age), notes))
            else:
                st.error("Please enter a pet name.")

    st.markdown("#### Your pets")
    if owner.pets:
        for p in owner.pets:
            st.markdown(
                f"""
<div class="card">
  <div class="title">{SPECIES_EMOJI.get(p.species, "🐾")} {escape(p.name)}</div>
  <div class="meta">{escape(p.species.title())} · {p.age} yr · {len(p.tasks)} task(s)
  {"· " + escape(p.notes) if p.notes else ""}</div>
</div>""",
                unsafe_allow_html=True,
            )
    else:
        st.info("No pets yet. Add your first one above.")

# --- Tasks -----------------------------------------------------------------
with tab_tasks:
    if owner.pets:
        with st.form("task_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            pet_choice = c1.selectbox("Pet", [p.name for p in owner.pets])
            title = c2.text_input("Task title", value="Morning walk")
            c1, c2, c3, c4 = st.columns(4)
            task_type = c1.selectbox("Type", [t.name.title() for t in TaskType])
            duration = c2.number_input("Minutes", min_value=1, max_value=240, value=20)
            priority = c3.selectbox("Priority", [p.name.title() for p in Priority])
            frequency = c4.selectbox("Frequency", [f.name.title() for f in Frequency], index=1)
            c1, c2 = st.columns(2)
            required = c1.checkbox("Required (e.g. meds)")
            use_pref = c2.checkbox("Has preferred time")
            p1, p2 = st.columns(2)
            pref_start = p1.time_input("Preferred from", value=time(8))
            pref_end = p2.time_input("Preferred until", value=time(9))
            if st.form_submit_button("Add task", type="primary", use_container_width=True):
                pet = next(p for p in owner.pets if p.name == pet_choice)
                try:
                    preferred = TimeSlot(pref_start, pref_end) if use_pref else None
                    pet.add_task(
                        Task(
                            title=title,
                            pet=pet,
                            type=TaskType[task_type.upper()],
                            duration_minutes=int(duration),
                            priority=Priority[priority.upper()],
                            frequency=Frequency[frequency.upper()],
                            preferred_time=preferred,
                            due_date=date.today() if frequency != "Daily" else None,
                            required=required,
                        )
                    )
                except ValueError as e:
                    st.error(str(e))
    else:
        st.info("Add a pet first, then you can give it tasks.")

    if all_tasks:
        st.markdown("#### Your tasks")
        f1, f2 = st.columns(2)
        pet_filter = f1.selectbox("Show pet", ["All"] + [p.name for p in owner.pets])
        status_filter = f2.selectbox("Show status", ["All", "Pending", "Completed"])
        browser = Scheduler(owner, st.session_state.availability)
        shown = browser.sort_by_time(
            browser.filter_tasks(
                completed={"All": None, "Pending": False, "Completed": True}[status_filter],
                pet_name=None if pet_filter == "All" else pet_filter,
            )
        )
        st.caption(f"{len(shown)} task(s), sorted by preferred time.")
        if shown:
            st.table(
                [
                    {
                        "Time": f"{t.preferred_time.start:%H:%M}-{t.preferred_time.end:%H:%M}"
                        if t.preferred_time
                        else "Anytime",
                        "Pet": t.pet.name,
                        "Task": t.title,
                        "Priority": t.priority.name.title(),
                        "Repeats": t.frequency.name.title(),
                        "Minutes": t.duration_minutes,
                        "Status": "Done" if t.is_completed else "Pending",
                    }
                    for t in shown
                ]
            )

        pending = [t for t in all_tasks if not t.is_completed]
        if pending:
            labels = {f"{t.pet.name}: {t.title}  (#{i + 1})": t for i, t in enumerate(pending)}
            done_choice = st.selectbox("Mark a task complete", list(labels))
            if st.button("Mark complete"):
                nxt = labels[done_choice].mark_complete()
                if nxt:
                    st.toast(f"Done! Next {nxt.frequency.name.lower()} copy is due {nxt.due_date}.")
                else:
                    st.toast("Done!")
                st.rerun()

# --- Availability ----------------------------------------------------------
with tab_time:
    st.caption("Time windows when you're free to do pet care.")
    with st.form("slot_form"):
        a1, a2 = st.columns(2)
        slot_start = a1.time_input("From", value=time(17))
        slot_end = a2.time_input("Until", value=time(18))
        if st.form_submit_button("Add window", type="primary", use_container_width=True):
            try:
                st.session_state.availability.append(TimeSlot(slot_start, slot_end))
            except ValueError as e:
                st.error(str(e))

    for s in st.session_state.availability:
        st.markdown(
            f"""
<div class="card"><div class="title">⏰ {s.start:%H:%M} – {s.end:%H:%M}</div>
<div class="meta">{s.duration_minutes()} minutes available</div></div>""",
            unsafe_allow_html=True,
        )
    if not st.session_state.availability:
        st.info("No availability set. Add a window above.")
    elif st.button("Clear availability"):
        st.session_state.availability = []
        st.rerun()

# --- Schedule --------------------------------------------------------------
with tab_plan:
    plan_day = st.date_input("Day", value=date.today())

    if st.button("✨ Generate schedule", type="primary", use_container_width=True):
        scheduler = Scheduler(owner, st.session_state.availability)
        plan = scheduler.schedule_tasks(plan_day)

        s1, s2 = st.columns(2)
        s1.metric("Tasks scheduled", len(plan.items))
        s2.metric("Minutes of care", plan.total_minutes())

        conflicts = scheduler.detect_conflicts(plan_day)
        if conflicts:
            st.warning(
                "**Scheduling conflicts:** these tasks want overlapping times. The plan below "
                "still fits everything it can, but some tasks were moved off their preferred time."
            )
            for message in conflicts:
                st.warning(message.replace("WARNING ", ""))
        else:
            st.success("No conflicts: no two tasks want the same time.")

        for i in plan.items:
            st.markdown(
                f"""
<div class="slot">
  <div class="time">{i.slot.start:%H:%M} – {i.slot.end:%H:%M}</div>
  <div class="title">{TYPE_EMOJI[i.task.type]} {escape(i.pet.name)}: {escape(i.task.title)}</div>
  <div class="why">Why: {escape(i.reason)}</div>
</div>""",
                unsafe_allow_html=True,
            )
        if not plan.items:
            st.info("Nothing could be scheduled.")
        if plan.has_missed_required():
            st.error("A required task did not fit in your availability!")
        for t in plan.unscheduled:
            st.warning(f"Couldn't fit: {t.pet.name} - {t.title} ({t.duration_minutes} min)")
        with st.expander("📝 Full explanation"):
            st.text(scheduler.explain_choices(plan))
    else:
        st.caption("Add pets, tasks and availability, then generate your plan.")
