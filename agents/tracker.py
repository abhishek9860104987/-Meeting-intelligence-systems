from datetime import datetime

def track_time(tasks):
    updated_tasks = []
    today = datetime.now().date()

    for t in tasks:
        deadline = t.get("deadline")

        if deadline:
            try:
                due_date = datetime.strptime(deadline, "%Y-%m-%d").date()
                days_left = (due_date - today).days

                if days_left < 0:
                    t["status"] = "Overdue"
                elif days_left == 0:
                    t["status"] = "Due Today"
                else:
                    t["time_left"] = f"{days_left} days left"

            except:
                t["time_left"] = "Invalid date"

        else:
            t["time_left"] = "No deadline"

        updated_tasks.append(t)

    return updated_tasks