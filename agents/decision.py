from typing import List, Dict, Any
from datetime import datetime, timedelta


# ===============================
# 🔥 MAIN DECISION FUNCTION
# ===============================
def apply_decision_logic(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    for t in tasks:

        desc = t.get("task", "").lower()
        confidence = t.get("confidence", 0.6)

        # ===============================
        # 🎯 PRIORITY ASSIGNMENT
        # ===============================
        if any(word in desc for word in ["urgent", "asap", "immediately"]):
            t["priority"] = "High"
        elif any(word in desc for word in ["bug", "issue", "fix"]):
            t["priority"] = "Medium"
        else:
            t["priority"] = "Low"

        # ===============================
        # ⏱ DEADLINE AUTO ASSIGN
        # ===============================
        if not t.get("deadline") or t["deadline"] in ["None", "", None]:

            if t["priority"] == "High":
                t["deadline"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            elif t["priority"] == "Medium":
                t["deadline"] = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
            else:
                t["deadline"] = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")

        # ===============================
        # 👤 OWNER FALLBACK
        # ===============================
        if not t.get("owner") or t["owner"] in ["Unassigned", "", None]:
            t["owner"] = "General Team"

        # ===============================
        # ⚠ RISK DETECTION
        # ===============================
        if confidence < 0.5:
            t["risk"] = "High"
        elif confidence < 0.75:
            t["risk"] = "Medium"
        else:
            t["risk"] = "Low"

        # ===============================
        # 🤖 STATUS + AUTOMATION (FIXED 🔥)
        # ===============================
        if t["owner"] != "General Team" and confidence >= 0.8:
            t["status"] = "CONFIRMED"
            t["automated"] = True   # 🔥 IMPORTANT

        elif t["owner"] != "General Team" and confidence >= 0.6:
            t["status"] = "AUTO_ASSIGNED"
            t["automated"] = True   # 🔥 IMPORTANT

        elif confidence < 0.5:
            t["status"] = "NEEDS_CLARIFICATION"
            t["needs_clarification"] = True
            t["automated"] = False

        else:
            t["status"] = "SUGGESTED"
            t["automated"] = False

    return tasks


# ===============================
# 🔥 AI INSIGHTS
# ===============================
def generate_decision_insights(tasks: List[Dict[str, Any]]) -> List[str]:

    insights = []

    total = len(tasks)
    high_priority = len([t for t in tasks if t.get("priority") == "High"])
    high_risk = len([t for t in tasks if t.get("risk") == "High"])

    # 🔥 FIXED: include CONFIRMED + AUTO_ASSIGNED
    automated = len([
        t for t in tasks
        if t.get("automated") == True
    ])

    if total == 0:
        return ["No tasks available"]

    if automated > 0:
        insights.append(f"🤖 {automated} tasks automated successfully")

    if high_priority > 0:
        insights.append(f"🚨 {high_priority} high-priority tasks require attention")

    if high_risk > 0:
        insights.append(f"⚠️ {high_risk} high-risk tasks detected")

    if automated == total:
        insights.append("🚀 Fully automated workflow")

    insights.append("💡 Focus on high-priority and high-risk tasks first")

    return insights


# ===============================
# 🔥 BUSINESS IMPACT (FIXED 🔥)
# ===============================
def calculate_decision_impact(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:

    if not tasks:
        return {
            "total_tasks": 0,
            "confirmed": 0,
            "automated": 0,
            "time_saved": 0,
            "cost_saved": 0,
            "automation_rate": 0
        }

    # ✅ ONLY CONFIRMED TASKS
    confirmed_tasks = [
        t for t in tasks if t.get("status") == "CONFIRMED"
    ]

    # ✅ CONFIRMED + AUTOMATED
    confirmed_automated = [
        t for t in confirmed_tasks
        if t.get("automated") == True or t.get("automated") == 1
    ]

    total = len(tasks)
    confirmed = len(confirmed_tasks)
    automated = len(confirmed_automated)

    # ⏱ Time saved
    time_saved = automated * 5

    # 💰 Cost saved
    cost_saved = time_saved * 0.5

    # 🤖 Automation %
    automation_rate = (
        (automated / confirmed) * 100 if confirmed > 0 else 0
    )

    return {
        "total_tasks": total,
        "confirmed_tasks": confirmed,
        "automated_tasks": automated,
        "time_saved": int(time_saved),
        "cost_saved": int(cost_saved),
        "automation_rate": round(automation_rate, 2)
    }


# ===============================
# 🔥 DASHBOARD OUTPUT
# ===============================
def get_decision_dashboard(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:

    updated_tasks = apply_decision_logic(tasks)

    insights = generate_decision_insights(updated_tasks)

    impact = calculate_decision_impact(updated_tasks)

    return {
        "tasks": updated_tasks,
        "insights": insights,
        "impact": impact
    }