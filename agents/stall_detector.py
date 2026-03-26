from datetime import datetime
from typing import List, Dict, Any
from database import get_all_tasks


# ===============================
# 🔥 MAIN FUNCTION (SECONDS BASED)
# ===============================
def detect_stalls(threshold_seconds: int = 86400) -> List[Dict[str, Any]]:

    stalled_tasks = []
    now = datetime.now()

    tasks = get_all_tasks()

    for row in tasks:
        try:
            task_id, task, owner, deadline, status, confidence, created_at, last_updated = row
        except:
            continue

        # 🚫 Skip completed tasks
        if str(status).lower() == "completed":
            continue

        # ⏱️ Parse time
        try:
            last_update_time = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
        except:
            continue

        # 🔥 FIX: use seconds
        inactivity_seconds = (now - last_update_time).total_seconds()

        if inactivity_seconds >= threshold_seconds:

            risk_level = get_risk_level(inactivity_seconds)

            stalled_tasks.append({
                "id": task_id,
                "task": task,
                "owner": owner if owner else "Unassigned",
                "seconds_inactive": int(inactivity_seconds),
                "risk": risk_level,
                "message": f"⚠️ Task stalled for {int(inactivity_seconds)} seconds",
                "suggestion": get_suggestion(inactivity_seconds, owner)
            })

    return stalled_tasks


# ===============================
# 🔥 RISK LEVEL (SECONDS BASED)
# ===============================
def get_risk_level(seconds: float) -> str:

    if seconds >= 30:
        return "CRITICAL"
    elif seconds >= 20:
        return "HIGH"
    elif seconds >= 10:
        return "MEDIUM"
    return "LOW"


# ===============================
# 🔥 SMART SUGGESTIONS
# ===============================
def get_suggestion(seconds: float, owner: str) -> str:

    if not owner or owner == "Unassigned":
        return "👤 Assign an owner immediately"

    if seconds >= 30:
        return "🚨 Escalate task to manager"

    elif seconds >= 20:
        return "⚡ Send reminder to owner"

    elif seconds >= 10:
        return "📩 Follow up with owner"

    return "✅ No action needed"


# ===============================
# 🔥 BUSINESS IMPACT
# ===============================
def calculate_stall_impact(stalled_tasks: List[Dict]) -> Dict[str, Any]:

    total_stalled = len(stalled_tasks)

    # Assume 10 seconds delay = 1 min productivity loss
    total_delay_mins = sum(t["seconds_inactive"] / 10 for t in stalled_tasks)

    cost_loss = (total_delay_mins / 60) * 500  # ₹

    return {
        "stalled_tasks": total_stalled,
        "delay_minutes": int(total_delay_mins),
        "cost_impact": int(cost_loss)
    }


# ===============================
# 🔥 AI INSIGHTS PANEL
# ===============================
def generate_stall_insights(stalled_tasks: List[Dict]) -> List[str]:

    insights = []

    total = len(stalled_tasks)

    if total == 0:
        return ["✅ No stalled tasks — workflow is smooth"]

    critical = len([t for t in stalled_tasks if t["risk"] == "CRITICAL"])
    high = len([t for t in stalled_tasks if t["risk"] == "HIGH"])

    if critical > 0:
        insights.append(f"🚨 {critical} critical stalled tasks need immediate attention")

    if high > 0:
        insights.append(f"⚠️ {high} high-risk tasks may cause delays")

    if total > 5:
        insights.append("📉 Overall productivity is impacted")

    insights.append("💡 Suggestion: Reassign or escalate stalled tasks")

    return insights


# ===============================
# 🔥 DASHBOARD OUTPUT
# ===============================
def get_stall_dashboard(threshold_seconds: int = 5):

    stalled = detect_stalls(threshold_seconds)

    impact = calculate_stall_impact(stalled)

    insights = generate_stall_insights(stalled)

    return {
        "stalled_tasks": stalled,
        "impact": impact,
        "insights": insights
    }