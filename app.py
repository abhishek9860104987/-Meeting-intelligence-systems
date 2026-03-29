from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd

from database import (
    init_db,
    insert_task,
    insert_clarification,
    get_tasks_by_project,
    get_all_projects,
    delete_project,
    update_task_owner,
    cleanup_case_insensitive_duplicates
)

# 🔥 AGENTS
from agents.extractor import extract_tasks
from agents.ownership import process_ownership
from agents.ambiguity import get_ambiguous
from agents.summary import generate_summary
from agents.tracker import track_time
from agents.clarifier import generate_questions

# 🔥 NEW AGENTS
from agents.decision import apply_decision_logic
from agents.stall_detector import detect_stalls
from agents.notifier import send_notifications
from agents.impact_tracker import impact_tracker

st_autorefresh(interval=10000, key="refresh")

init_db()

st.set_page_config(layout="wide")
st.title("🧠Meeting intelligence systems")

# ===============================
# 📁 Sidebar
# ===============================
st.sidebar.header("📁 Project Management")

projects = get_all_projects()
selected_project = st.sidebar.selectbox("Select Project", [""] + projects)
new_project = st.sidebar.text_input("Create New Project")

if selected_project:
    st.sidebar.markdown("---")

    if st.sidebar.checkbox("🗑️ Confirm Delete Project"):
        if st.sidebar.button("Delete Project"):
            delete_project(selected_project)
            st.sidebar.success("Project deleted!")
            st.rerun()

    st.sidebar.markdown("---")

    if st.sidebar.button("🧹 Clean Duplicates"):
        deleted = cleanup_case_insensitive_duplicates(selected_project)
        if deleted > 0:
            st.sidebar.success(f"Cleaned {deleted} duplicates!")
            st.rerun()
        else:
            st.sidebar.info("No duplicates found")

project_name = new_project if new_project else selected_project

if project_name:
    st.sidebar.success(f"📂 Loaded: {project_name}")

run = st.sidebar.button("🚀 Run AI")
transcript = st.text_area("📋 Paste Transcript")

# ===============================
# 🚀 RUN PIPELINE
# ===============================
if run and project_name:

    if not transcript.strip():
        st.error("❌ Please enter transcript")
    else:
        tasks = extract_tasks(transcript)
        tasks = process_ownership(tasks, project_name)
        tasks = apply_decision_logic(tasks)
        tasks = track_time(tasks)

        st.session_state.tasks = tasks

        for t in tasks:
            insert_task(t, project_name)

            if t.get("needs_clarification"):
                insert_clarification(t, project_name)

        st.success("✅ Tasks processed successfully")

# ===============================
# 📊 FETCH TASKS
# ===============================
def fetch_tasks(project):
    rows = get_tasks_by_project(project)

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows, columns=[
        "task", "owner", "deadline", "status",
        "confidence", "project", "last_updated",
        "automated"
    ])

df = fetch_tasks(project_name)

if project_name and not df.empty:
    df["automated"] = df["automated"].fillna(0)
    st.session_state.tasks = df.to_dict("records")

# ===============================
# 🖥️ DISPLAY
# ===============================
if project_name and not df.empty:

    st.subheader("📊 All Tasks")

    df["confidence_level"] = df["confidence"].apply(
        lambda c: "🟢 High" if c >= 0.8 else "🟡 Medium" if c >= 0.5 else "🔴 Low"
    )

    def style_status(val):
        if val == "CONFIRMED":
            return "color: yellow"
        elif val == "NEEDS_CLARIFICATION":
            return "color: red"
        elif val == "AUTO_ASSIGNED":
            return "color: pink"
        return ""

    styled_df = df.style.map(style_status, subset=["status"])
    st.dataframe(styled_df, width="stretch")

    tasks = st.session_state.get("tasks", df.to_dict("records"))

# ===============================
# 📈 TASK INSIGHTS (SAFE FIX 🔥)
# ===============================
st.subheader("📈 Task Insights")

if df is not None and not df.empty and "status" in df.columns:
    status_counts = df["status"].value_counts()
else:
    status_counts = {}

# 🔥 stalled count (safe)
stalled_tasks = detect_stalls()
stalled_count = len(stalled_tasks)

col1, col2, col3, col4 = st.columns(4)
col1.metric("🚨 Stalled", stalled_count)
col2.metric("⚠ Suggested", status_counts.get("SUGGESTED", 0))
col3.metric("❓ Need Clarification", status_counts.get("NEEDS_CLARIFICATION", 0))
col4.metric("✅ Confirmed", status_counts.get("CONFIRMED", 0))



stalled_tasks = detect_stalls()
# ===============================
# 💰 BUSINESS IMPACT
# ===============================
st.subheader("💰 Business Impact")

tasks = st.session_state.get("tasks", [])
dashboard = impact_tracker.get_dashboard(tasks)
metrics = dashboard["metrics"]

col1, col2, col3 = st.columns(3)
col1.metric("⏱ Time Saved", metrics["time_saved"])
col2.metric("💰 Cost Saved", int(metrics["cost_saved"]))
col3.metric("📊 Automation %", f"{metrics['automation_rate']:.1f}%")



# ===============================
# 🚨 STALLED TASKS
# ===============================
st.subheader("🚨 Stalled Tasks")


# ===============================
# 📊 GRAPH + NOTIFICATIONS SIDE BY SIDE
# ===============================
col1, col2 = st.columns([2, 1])

# LEFT: GRAPH
with col1:

    st.subheader("📈 Stall Duration Trend")

    import matplotlib.pyplot as plt

    sorted_tasks = sorted(stalled_tasks, key=lambda x: x["seconds_inactive"])
    stall_times = [s["seconds_inactive"] for s in sorted_tasks]
    task_index = list(range(1, len(stall_times) + 1))

    num_tasks = len(task_index)

    width = min(4, max(2.5, num_tasks * 0.4))
    height = min(4, max(2.5, num_tasks * 0.3))

    fig, ax = plt.subplots(figsize=(width, height))

    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    ax.plot(task_index, stall_times, marker='o', linewidth=1)

    ax.set_title("Trend", fontsize=7, color="yellow")
    ax.set_xlabel("Task", fontsize=6, color="yellow")
    ax.set_ylabel("Sec", fontsize=6, color="yellow")

    ax.tick_params(axis='both', labelsize=5, colors="yellow")

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.grid(alpha=0.2)

    plt.tight_layout(pad=0.5)

    st.pyplot(fig, use_container_width=False)

    # Stalled list
    if not stalled_tasks:
        st.success("No stalled tasks")

    for s in stalled_tasks:
        st.write(f"{s['task']} - {s['seconds_inactive']} sec")

# RIGHT: NOTIFICATIONS
with col2:

    st.subheader("📩 Notifications")

    notifications = send_notifications([], stalled_tasks)

    if not notifications:
        st.info("No notifications")

    for n in notifications:
        st.write(f"📩 {n['message']}")



# ===============================
# ❗ CLARIFICATION PANEL
# ===============================
st.subheader("❗ Tasks Needing Clarification")

ambiguous_tasks = get_ambiguous(tasks)

if not ambiguous_tasks:
    st.success("🎉 No ambiguous tasks")

for idx, t in enumerate(ambiguous_tasks):

    st.error(f"❓ {t['task']}")
    st.write(f"**Owner:** {t.get('owner', 'Unassigned')}")
    st.write(f"**Confidence:** {t.get('confidence', 0)}")

    if t.get("confidence", 1) < 0.5:
        st.info("💡 Reason: Low confidence, vague task")
    else:
        st.info("💡 Reason: Needs clarification")

    questions = generate_questions(t)
    for q in questions:
        st.write(f"- {q}")

    if not df.empty:
        owners = list(df["owner"].unique())
        owners = [o for o in owners if o != "Unassigned"]
    else:
        owners = []

    selected_owner = st.selectbox(
        f"Assign owner for: {t['task']}",
        ["Select"] + owners,
        key=f"{t['task']}_{idx}"
    )

    if selected_owner != "Select":
        update_task_owner(t["task"], selected_owner, project_name)
        st.success(f"Assigned to {selected_owner}")
        st.rerun()

# ===============================
# 📄 SUMMARY
# ===============================
st.subheader("📄 Meeting Summary")

summary = generate_summary(tasks)
st.success(summary)