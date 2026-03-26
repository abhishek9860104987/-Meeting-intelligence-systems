from datetime import datetime

def check_escalation(tasks):
    escalated = []
    today = datetime.now().date()

    for t in tasks:
        task_name = t.get("task", "")
        owner = t.get("owner", "Unassigned")
        status = t.get("status", "")
        deadline = t.get("deadline", "")

        # Skip completed tasks
        if status.lower() == "completed":
            continue

        # 🚨 HIGH PRIORITY → Overdue
        if status == "Overdue":
            escalated.append({
                "task": task_name,
                "level": "High",
                "notify": ["Owner", "Manager"],
                "message": f"🚨 Task overdue! Escalated to manager and {owner}"
            })

        # ⚠️ MEDIUM → Due Today / Due Soon
        elif status in ["Due Today", "Due Soon"]:
            escalated.append({
                "task": task_name,
                "level": "Medium",
                "notify": ["Owner"],
                "message": f"⚠️ Task approaching deadline. Reminder sent to {owner}"
            })

        # ⚠️ LOW → Missing or invalid deadline
        else:
            if not deadline:
                escalated.append({
                    "task": task_name,
                    "level": "Low",
                    "notify": ["Owner"],
                    "message": f"⚠️ No deadline assigned for task"
                })
            else:
                try:
                    datetime.strptime(deadline, "%Y-%m-%d")
                except:
                    escalated.append({
                        "task": task_name,
                        "level": "Low",
                        "notify": ["Owner"],
                        "message": f"⚠️ Invalid deadline format"
                    })

    return escalated