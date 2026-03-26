def process_ownership(tasks, project_name=None):
    """
    Improved ownership logic with:
    - invalid owner filtering
    - vague task handling
    - respects extractor flags
    """

    # 🔥 Invalid owners (must match extractor)
    INVALID_NAMES = {
        "Database", "System", "UI", "Backend", "Frontend"
    }

    # 🔥 Role keywords
    ROLE_HINTS = {
        "frontend": ["frontend", "ui"],
        "backend": ["backend", "api"],
        "database": ["database", "db"],
        "testing": ["test", "testing", "qa"]
    }

    # 🔥 Vague detection
    def is_vague(text):
        text = text.lower()
        return any(w in text for w in [
            "everything", "stuff", "things", "something",
            "anything", "fix it", "handle it", "do it"
        ])

    # 🔥 Step 1: Build role map
    role_map = {}

    for t in tasks:
        text = t.get("task", "").lower()
        owner = t.get("owner")

        if owner and owner != "Unassigned" and owner not in INVALID_NAMES:
            for role, keywords in ROLE_HINTS.items():
                if any(k in text for k in keywords):
                    role_map[role] = owner

    # 🔥 Step 2: Process tasks
    for t in tasks:
        owner = t.get("owner")
        task_text = t.get("task", "").strip()

        # ❗ Invalid task
        if not task_text:
            t.update({
                "owner": "Unassigned",
                "status": "NEEDS_CLARIFICATION",
                "message": "Task is unclear",
                "confidence": 0.0
            })
            continue

        # 🔥 Fix invalid owner
        if owner in INVALID_NAMES:
            owner = None

        # 🔥 Case 1: Already has valid owner
        if owner and owner != "Unassigned":

            # ❗ Check vague task
            if is_vague(task_text):
                t.update({
                    "owner": owner,
                    "status": "NEEDS_CLARIFICATION",
                    "message": "Task is too vague",
                    "confidence": 0.4
                })
            else:
                t.update({
                    "owner": owner,
                    "status": "CONFIRMED",
                    "message": "Owner clearly specified",
                    "confidence": 1.0
                })
            continue

        # 🔥 Case 2: Role-based assignment
        assigned = False

        for role, keywords in ROLE_HINTS.items():
            if any(k in task_text.lower() for k in keywords):
                if role in role_map:
                    t.update({
                        "owner": role_map[role],
                        "status": "AUTO_ASSIGNED",
                        "message": "Assigned based on role context",
                        "confidence": 0.95
                    })
                    assigned = True
                    break

        # 🔥 Case 3: Still unassigned
        if not assigned:
            t.update({
                "owner": "Unassigned",
                "status": "NEEDS_CLARIFICATION",
                "message": "Owner not specified",
                "confidence": 0.0
            })

    return tasks