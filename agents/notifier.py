from typing import List, Dict, Any
from datetime import datetime


# ===============================
# 🔥 SEND NOTIFICATIONS
# ===============================
def send_notifications(escalated_tasks: List[Dict], stalled_tasks: List[Dict]):

    notifications = []

    # 🚨 Escalation notifications
    for e in escalated_tasks:
        for target in e.get("notify", []):
            notifications.append({
                "task": e["task"],
                "to": target,
                "type": "ESCALATION",
                "priority": "HIGH",
                "timestamp": datetime.now().isoformat(),
                "message": f"📩 {target} notified: {e.get('message', 'Escalation')}"
            })

    # ⏳ Stall notifications
    for s in stalled_tasks:

        seconds = s.get("seconds_inactive", 0)  # ✅ FIXED
        risk = s.get("risk", "MEDIUM")

        # 👤 Owner notification
        notifications.append({
            "task": s["task"],
            "to": s.get("owner", "Owner"),
            "type": "STALL",
            "priority": risk,
            "timestamp": datetime.now().isoformat(),
            "message": f"📩 Owner notified: Task stalled for {seconds} seconds"
        })

        # 👨‍💼 Manager escalation
        if risk in ["HIGH", "CRITICAL"]:
            notifications.append({
                "task": s["task"],
                "to": "Manager",
                "type": "ESCALATION",
                "priority": "HIGH",
                "timestamp": datetime.now().isoformat(),
                "message": "📩 Manager notified: escalation triggered"
            })

    return notifications


# ===============================
# 📊 IMPACT
# ===============================
def calculate_notification_impact(notifications: List[Dict]):

    total = len(notifications)
    high_priority = len([n for n in notifications if n["priority"] in ["HIGH", "CRITICAL"]])

    cost_impact = total * 100  # ₹ estimate

    return {
        "total_notifications": total,
        "high_priority": high_priority,
        "cost_impact": cost_impact
    }


# ===============================
# 🧠 AI INSIGHTS
# ===============================
def generate_notification_insights(notifications: List[Dict]):

    insights = []

    if not notifications:
        return ["✅ No notifications"]

    escalations = len([n for n in notifications if n["type"] == "ESCALATION"])

    if escalations > 3:
        insights.append("🚨 High escalation rate detected")

    if len(notifications) > 10:
        insights.append("📩 High notification volume")

    insights.append("💡 Improve task completion to reduce alerts")

    return insights


# ===============================
# 🔥 DASHBOARD FUNCTION
# ===============================
def get_notification_dashboard(escalated_tasks, stalled_tasks):

    notifications = send_notifications(escalated_tasks, stalled_tasks)
    impact = calculate_notification_impact(notifications)
    insights = generate_notification_insights(notifications)

    return {
        "notifications": notifications,
        "impact": impact,
        "insights": insights
    }