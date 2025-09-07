# app.py — Student Study Tracker (date-first, auto-carry next day, progress bar)
import streamlit as st
import pandas as pd
import datetime as dt
from pathlib import Path
import uuid

# ---------------------- Setup ----------------------
st.set_page_config(page_title="Student Study Tracker", layout="wide")
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
TASKS_CSV = DATA_DIR / "tasks.csv"
STUDENTS_CSV = DATA_DIR / "students.csv"
META_CSV = DATA_DIR / "meta.csv"  # to remember last carry run per student per date

TASK_COLUMNS = [
    "id","student","date","subject","task","planned_hours","notes",
    "status","actual_hours","reflection","created_at","carried_from"
]

def load_df(path: Path, columns: list[str]) -> pd.DataFrame:
    if path.exists():
        df = pd.read_csv(path)
        for c in columns:
            if c not in df.columns:
                df[c] = None
        return df[columns]
    return pd.DataFrame(columns=columns)

def save_df(df: pd.DataFrame, path: Path):
    df.to_csv(path, index=False)

def load_tasks() -> pd.DataFrame:
    return load_df(TASKS_CSV, TASK_COLUMNS)

def save_tasks(df: pd.DataFrame):
    save_df(df, TASKS_CSV)

def load_students() -> pd.DataFrame:
    cols = ["student","physics_current","addmaths_current","physics_target","addmaths_target","created_at"]
    return load_df(STUDENTS_CSV, cols)

def save_students(df: pd.DataFrame):
    save_df(df, STUDENTS_CSV)

def load_meta() -> pd.DataFrame:
    cols = ["key","value"]
    return load_df(META_CSV, cols)

def save_meta(df: pd.DataFrame):
    save_df(df, META_CSV)

def get_meta(key: str, default: str|None=None) -> str|None:
    m = load_meta()
    row = m[m["key"]==key]
    if row.empty: return default
    return str(row.iloc[0]["value"])

def set_meta(key: str, value: str):
    m = load_meta()
    if (m["key"]==key).any():
        m.loc[m["key"]==key,"value"] = value
    else:
        m.loc[len(m)] = [key, value]
    save_meta(m)

# ---------------------- Carry-Forward (previous day -> selected day) ----------------------
def carry_forward_from_previous_day(selected_date: dt.date, student: str):
    """
    When the user picks a date D in the sidebar:
    - Copy all tasks from D-1 that are not 'Done' (i.e., Pending or Skipped) into D.
    - Do this ONCE per (student, D).
    """
    if not student or not selected_date:
        return
    prev_day = selected_date - dt.timedelta(days=1)
    # guard: only run once per student per target date
    flag_key = f"carry_{student}_{selected_date.isoformat()}"
    if get_meta(flag_key, "") == "done":
        return

    tasks = load_tasks()
    if tasks.empty:
        set_meta(flag_key, "done")
        return

    # Filter yesterday's tasks for this student which are not Done
    mask_y = (
        (tasks["student"]==student) &
        (pd.to_datetime(tasks["date"]).dt.date == prev_day) &
        (~tasks["status"].isin(["Done"]))  # Pending or Skipped get carried
    )
    y_tasks = tasks[mask_y].copy()

    if not y_tasks.empty:
        copies = y_tasks.copy()
        copies["id"] = [str(uuid.uuid4()) for _ in range(len(copies))]
        copies["date"] = str(selected_date)
        copies["status"] = "Pending"
        copies["actual_hours"] = None
        copies["reflection"] = None
        copies["created_at"] = dt.datetime.now().isoformat(timespec="seconds")
        copies["carried_from"] = prev_day.isoformat()
        tasks = pd.concat([tasks, copies], ignore_index=True)
        save_tasks(tasks)

    set_meta(flag_key, "done")

# ---------------------- Session defaults ----------------------
if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "results" not in st.session_state:
    st.session_state.results = {"Physics": None, "Add Maths": None}
if "targets" not in st.session_state:
    st.session_state.targets = {"Physics": None, "Add Maths": None}

# ---------------------- UI: Title & Onboarding ----------------------
st.title("📚 Student Study Tracker")

with st.expander("Onboarding • Student + Targets", expanded=True if not st.session_state.student_name else False):
    with st.form("onboarding"):
        st.session_state.student_name = st.text_input("Student Name", value=st.session_state.student_name)
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.results["Physics"]   = st.number_input("Current Physics (%)", 0, 100, value=st.session_state.results["Physics"] or 0)
            st.session_state.targets["Physics"]   = st.number_input("Target Physics (%)",  0, 100, value=st.session_state.targets["Physics"] or 0)
        with c2:
            st.session_state.results["Add Maths"] = st.number_input("Current Add Maths (%)", 0, 100, value=st.session_state.results["Add Maths"] or 0)
            st.session_state.targets["Add Maths"] = st.number_input("Target Add Maths (%)",  0, 100, value=st.session_state.targets["Add Maths"] or 0)
        submitted = st.form_submit_button("Save / Update Profile")
    if submitted and st.session_state.student_name.strip():
        students = load_students()
        students = students[students["student"] != st.session_state.student_name]  # keep unique
        students.loc[len(students)] = [
            st.session_state.student_name,
            st.session_state.results["Physics"],
            st.session_state.results["Add Maths"],
            st.session_state.targets["Physics"],
            st.session_state.targets["Add Maths"],
            dt.datetime.now().isoformat(timespec="seconds"),
        ]
        save_students(students)
        st.success("Saved! Use the left sidebar to choose your tracking date.")

# ---------------------- Sidebar (Date + Info) ----------------------
st.sidebar.header("📅 Choose a Date (required)")
today = dt.date.today()
selected_date = st.sidebar.date_input("Track date", today)
st.sidebar.divider()

if st.session_state.student_name:
    st.sidebar.write(f"**Student:** {st.session_state.student_name}")
    st.sidebar.write(f"Physics: {st.session_state.results['Physics']} ➜ Target {st.session_state.targets['Physics']}")
    st.sidebar.write(f"Add Maths: {st.session_state.results['Add Maths']} ➜ Target {st.session_state.targets['Add Maths']}")

# IMPORTANT: run carry forward for the chosen date (copy from yesterday -> chosen date)
if st.session_state.student_name:
    carry_forward_from_previous_day(selected_date, st.session_state.student_name)

# ---------------------- Tabs ----------------------
tab1, tab2, tab3, tab4 = st.tabs(["🗓️ Daily Plan", "✅ Mark Completion", "📈 Progress", "⚙️ Settings"])

# ---------------------- Tab 1: Daily Plan ----------------------
with tab1:
    st.subheader("Plan Tasks for the Selected Date")
    if not st.session_state.student_name.strip():
        st.warning("Enter your name in Onboarding first.")
    else:
        st.caption(f"Adding tasks for: **{selected_date.isoformat()}**")
        c1, c2, c3 = st.columns([2,1,1])
        with c1:
            task_name = st.text_input("Task name (e.g., 'Chapter 3 Kinematics Qs')")
        with c2:
            subject = st.selectbox("Subject", ["Physics", "Add Maths"])
        with c3:
            hours = st.number_input("Planned hours", min_value=0.0, max_value=24.0, step=0.5, value=1.0)
        notes = st.text_area("Notes (optional)")

        add = st.button("➕ Add Task")
        if add:
            if not task_name.strip():
                st.error("Task name cannot be empty.")
            else:
                tasks = load_tasks()
                tasks.loc[len(tasks)] = [
                    str(uuid.uuid4()),
                    st.session_state.student_name,
                    selected_date.isoformat(),
                    subject,
                    task_name.strip(),
                    float(hours),
                    notes.strip() if notes else "",
                    "Pending",
                    None,  # actual_hours
                    None,  # reflection
                    dt.datetime.now().isoformat(timespec="seconds"),
                    None   # carried_from
                ]
                save_tasks(tasks)
                st.success("Task saved.")
                st.rerun()

        # Show table for selected date
        tasks = load_tasks()
        mask = (
            (tasks["student"]==st.session_state.student_name) &
            (pd.to_datetime(tasks["date"]).dt.date==selected_date)
        )
        st.caption("Tasks for this date")
        st.dataframe(
            tasks[mask][["subject","task","planned_hours","status","carried_from"]].reset_index(drop=True),
            use_container_width=True
        )

# ---------------------- Tab 2: Mark Completion ----------------------
with tab2:
    st.subheader(f"Mark Tasks — {selected_date.isoformat()}")
    tasks = load_tasks()
    mask = (
        (tasks["student"]==st.session_state.student_name) &
        (pd.to_datetime(tasks["date"]).dt.date==selected_date)
    )
    day_tasks = tasks[mask].copy()

    if day_tasks.empty:
        st.info("No tasks for this date. Add tasks in the Daily Plan tab.")
    else:
        for i, row in day_tasks.sort_values(by=["subject","created_at"]).iterrows():
            with st.form(f"complete_{row['id']}"):
                st.markdown(f"**{row['subject']}** — {row['task']}")
                c1, c2, c3 = st.columns([1,1,2])
                with c1:
                    status = st.selectbox("Status", ["Pending","Done","Skipped"],
                                          index=["Pending","Done","Skipped"].index(row["status"]))
                with c2:
                    actual = st.number_input("Actual hrs", min_value=0.0, max_value=24.0, step=0.5,
                                             value=float(row["actual_hours"]) if pd.notna(row["actual_hours"]) else 0.0)
                with c3:
                    refl = st.text_input("Reflection / notes", value=row["reflection"] if pd.notna(row["reflection"]) else "")
                updated = st.form_submit_button("Save")
            if updated:
                tasks.loc[tasks["id"]==row["id"], ["status","actual_hours","reflection"]] = [status, actual, refl]
                save_tasks(tasks)
                st.success("Updated.")
                st.rerun()

# ---------------------- Tab 3: Progress ----------------------
with tab3:
    st.subheader("Progress Overview")
    tasks = load_tasks()
    if tasks.empty or not st.session_state.student_name:
        st.info("No data yet.")
    else:
        me = tasks[tasks["student"]==st.session_state.student_name].copy()
        if me.empty:
            st.info("No data yet.")
        else:
            me["date"] = pd.to_datetime(me["date"]).dt.date

            # --- Progress bar (selected date completion %) ---
            day = me[me["date"]==selected_date]
            if not day.empty:
                completion_rate = (day["status"]=="Done").mean()
                st.write(f"**Selected Date:** {selected_date.isoformat()} — Completion: {int(completion_rate*100)}%")
                st.progress(float(completion_rate))
            else:
                st.write(f"**Selected Date:** {selected_date.isoformat()} — no tasks yet.")

            st.divider()

            # --- Daily Completion % chart ---
            comp = me.groupby("date")["status"].apply(lambda s: (s=="Done").mean()*100).reset_index(name="Completion %")
            st.write("**Daily Completion %**")
            if not comp.empty:
                st.line_chart(comp.set_index("date"))

            # --- Study hours by subject (actual if present else planned) ---
            me["study_hours"] = me.apply(
                lambda r: float(r["actual_hours"]) if pd.notna(r["actual_hours"]) else float(r["planned_hours"] or 0.0),
                axis=1
            )
            hours = me.groupby(["date","subject"])["study_hours"].sum().unstack(fill_value=0)
            st.write("**Study Hours by Subject**")
            if not hours.empty:
                st.area_chart(hours)

            st.write("**Recent Tasks**")
            st.dataframe(
                me.sort_values("date", ascending=False)[
                    ["date","subject","task","status","planned_hours","actual_hours","carried_from"]
                ].head(30),
                use_container_width=True
            )

# ---------------------- Tab 4: Settings ----------------------
with tab4:
    st.subheader("Export / Maintenance")
    tasks = load_tasks()
    colA, colB = st.columns(2)
    with colA:
        st.download_button("⬇️ Download tasks.csv", data=tasks.to_csv(index=False),
                           file_name="tasks.csv", mime="text/csv")
    with colB:
        if st.button("🧹 Clear ALL my tasks (careful)"):
            tasks = tasks[tasks["student"]!=st.session_state.student_name]
            save_tasks(tasks)
            st.warning("Your tasks were cleared.")
            st.rerun()
