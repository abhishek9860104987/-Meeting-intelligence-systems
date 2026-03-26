from utils.groq_client import call_groq


# ===============================
# 🔥 MAIN SUMMARY FUNCTION
# ===============================
def generate_summary(tasks):

    if not tasks:
        return "No tasks available to summarize."

    # ===============================
    # 📊 Basic Metrics (FIXED 🔥)
    # ===============================
    total = len(tasks)

    confirmed_tasks = [
        t for t in tasks if t.get("status") == "CONFIRMED"
    ]

    automated_tasks = [
        t for t in confirmed_tasks
        if t.get("automated") == True or t.get("automated") == 1
    ]

    pending = len([
        t for t in tasks if t.get("status") != "CONFIRMED"
    ])

    confirmed = len(confirmed_tasks)
    automated = len(automated_tasks)

    # ===============================
    # 💰 Business Impact (FIXED 🔥)
    # ===============================
    time_saved = automated * 5   # aligned with impact_tracker
    cost_saved = time_saved * 0.5

    # ===============================
    # 🧠 Prompt
    # ===============================
    prompt = f"""
You are an AI project assistant.

Generate a professional meeting summary with the following sections:

1. Overview
2. Key Tasks
3. Risks / Issues
4. AI Insights
5. Business Impact

Tasks:
{tasks}

Metrics:
- Total Tasks: {total}
- Confirmed Tasks: {confirmed}
- Automated Tasks: {automated}
- Pending Tasks: {pending}
- Time Saved: {time_saved} minutes
- Cost Saved: ₹{int(cost_saved)}

Keep it concise, clear, and professional.
"""

    # ===============================
    # 🤖 LLM CALL
    # ===============================
    try:
        return call_groq(prompt)

    except Exception:
        return fallback_summary(
            tasks, total, confirmed, automated, pending, time_saved, cost_saved
        )


# ===============================
# 🔥 FALLBACK SUMMARY (IMPROVED)
# ===============================
def fallback_summary(tasks, total, confirmed, automated, pending, time_saved, cost_saved):

    summary = f"""
📄 MEETING SUMMARY

🔹 Total Tasks: {total}
🔹 Confirmed: {confirmed}
🔹 Automated: {automated}
🔹 Pending: {pending}

⏱ Time Saved: {time_saved} mins
💰 Cost Saved: ₹{int(cost_saved)}

⚠ Pending tasks require attention.

💡 Suggestion:
- Assign unclear tasks
- Improve automation coverage
"""

    return summary


# ===============================
# 🔥 EXTRA: AI INSIGHTS ONLY (FIXED)
# ===============================
def generate_summary_insights(tasks):

    if not tasks:
        return ["No tasks available"]

    confirmed_tasks = [
        t for t in tasks if t.get("status") == "CONFIRMED"
    ]

    automated_tasks = [
        t for t in confirmed_tasks
        if t.get("automated") == True or t.get("automated") == 1
    ]

    total = len(tasks)
    confirmed = len(confirmed_tasks)
    automated = len(automated_tasks)

    insights = []

    if confirmed > 0:
        automation_rate = (automated / confirmed) * 100
    else:
        automation_rate = 0

    if automation_rate > 70:
        insights.append("🚀 High automation efficiency")
    else:
        insights.append("⚡ Automation can be improved")

    if total > 10:
        insights.append("📊 Large number of tasks detected")

    if confirmed < total:
        insights.append("⚠ Some tasks still need confirmation")

    return insights