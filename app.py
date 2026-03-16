import streamlit as st
from datetime import date, time
from pawpal_system import Activity, Frequency, Owner, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Session state bootstrap ───────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = Owner(first_name="Jordan", last_name="", phone="000-000-0000")
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

# ── Add a pet ─────────────────────────────────────────────────────────────────
st.subheader("My Pets")

with st.form("add_pet_form", clear_on_submit=True):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        new_pet_name = st.text_input("Name", placeholder="Mochi")
    with c2:
        new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
    with c3:
        new_pet_breed = st.text_input("Breed", placeholder="Shiba Inu")
    with c4:
        new_pet_bday = st.date_input("Birthday", value=date.today())
    submitted = st.form_submit_button("Add pet")

if submitted:
    if new_pet_name.strip():
        owner.add_pet(Pet(
            name=new_pet_name.strip(),
            birthday=new_pet_bday,
            type=new_pet_species,
            breed=new_pet_breed.strip(),
        ))
        st.success(f"{new_pet_name.strip()} added!")
    else:
        st.error("Pet name is required.")

# ── Pet selector ──────────────────────────────────────────────────────────────
if not owner.pets:
    st.info("No pets yet. Add one above to get started.")
    st.stop()

pet_names = [p.name for p in owner.pets]
selected_name = st.selectbox("Select pet", pet_names, key="selected_pet")
pet: Pet = next(p for p in owner.pets if p.name == selected_name)

st.caption(f"**{pet.name}** · {pet.type} · {pet.breed} · born {pet.birthday}")

st.divider()

# ── Add a task ────────────────────────────────────────────────────────────────
st.subheader(f"Tasks for {pet.name}")

with st.form("add_task_form", clear_on_submit=True):
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        start_time_input = st.time_input("Start time", value=time(8, 0))
    with col4:
        frequency = st.selectbox(
            "Frequency", list(Frequency),
            format_func=lambda f: f.value.replace("_", " ").title(),
        )
    with col5:
        scheduled_date = st.date_input("Date (one-time/weekly)", value=date.today())
    add_task = st.form_submit_button("Add task")

if add_task:
    scheduler.add_task(pet, Activity(
        name=task_title,
        description=task_title,
        start_time=start_time_input,
        duration=int(duration),
        frequency=frequency,
        scheduled_date=scheduled_date,
    ))

# ── Filter + display tasks ────────────────────────────────────────────────────
freq_filter = st.selectbox(
    "Filter by frequency",
    [None] + list(Frequency),
    format_func=lambda f: "All" if f is None else f.value.replace("_", " ").title(),
    key="freq_filter",
)

if freq_filter is None:
    display_tasks = scheduler.get_tasks(pet)
else:
    display_tasks = scheduler.get_tasks_by_frequency(pet, freq_filter)

if display_tasks:
    st.table([
        {
            "Task": t.name,
            "Start": t.start_time.strftime("%I:%M %p"),
            "Duration (min)": t.duration,
            "Frequency": t.frequency.value,
            "Date": str(t.scheduled_date) if t.scheduled_date else "—",
            "Done": "Yes" if t.is_complete else "No",
        }
        for t in display_tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

# ── Mark task complete ────────────────────────────────────────────────────────
pending = scheduler.get_pending_tasks(pet)
if pending:
    task_to_complete = st.selectbox(
        "Mark task as complete",
        pending,
        format_func=lambda t: f"{t.name} ({t.start_time.strftime('%I:%M %p')} · {t.frequency.value})",
        key="complete_selector",
    )
    if st.button("Mark complete"):
        scheduler.complete_task(pet, task_to_complete)
        st.rerun()

# ── Conflict warnings ─────────────────────────────────────────────────────────
conflicts = scheduler.detect_conflicts(pet)
if conflicts:
    st.warning(f"⚠️ {len(conflicts)} scheduling conflict(s) for {pet.name}:")
    for a, b in conflicts:
        st.write(f"  • **{a.name}** ({a.start_time.strftime('%I:%M %p')}) overlaps **{b.name}** ({b.start_time.strftime('%I:%M %p')})")

cross_conflicts = scheduler.detect_all_conflicts()
if cross_conflicts:
    st.warning(f"⚠️ {len(cross_conflicts)} cross-pet conflict(s):")
    for pa, ta, pb, tb in cross_conflicts:
        st.write(f"  • **{pa.name}**: {ta.name} ({ta.start_time.strftime('%I:%M %p')}) overlaps **{pb.name}**: {tb.name} ({tb.start_time.strftime('%I:%M %p')})")

st.divider()

# ── Generate schedule ─────────────────────────────────────────────────────────
st.subheader("Build Schedule")
schedule_date = st.date_input("View schedule for date", value=date.today(), key="schedule_date")

if st.button("Generate schedule"):
    day_tasks = scheduler.get_tasks_for_date(pet, schedule_date)
    if day_tasks:
        st.success(f"Schedule for {pet.name} on {schedule_date.strftime('%A, %B %d')}:")
        st.table([
            {
                "Task": t.name,
                "Start": t.start_time.strftime("%I:%M %p"),
                "End": t.end_time().strftime("%I:%M %p"),
                "Duration (min)": t.duration,
                "Frequency": t.frequency.value,
                "Done": "Yes" if t.is_complete else "No",
            }
            for t in day_tasks
        ])
    else:
        st.info("No tasks scheduled for that date.")

# ── Upcoming & overdue ────────────────────────────────────────────────────────
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Upcoming (next 60 min)")
    upcoming = scheduler.get_upcoming_tasks(pet, within_minutes=60)
    if upcoming:
        for t in upcoming:
            st.write(f"• **{t.name}** at {t.start_time.strftime('%I:%M %p')}")
    else:
        st.caption("Nothing coming up in the next hour.")

with col_b:
    st.subheader("Overdue Today")
    overdue = scheduler.get_overdue_tasks(pet)
    if overdue:
        for t in overdue:
            st.write(f"• **{t.name}** was at {t.start_time.strftime('%I:%M %p')}")
    else:
        st.caption("No overdue tasks.")
