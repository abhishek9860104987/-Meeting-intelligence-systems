def get_ambiguous(tasks):
    """
    Returns tasks that need attention based on:
    - status
    - low confidence
    - missing owner
    - explicit clarification flag
    - vague wording
    - unclear deadlines
    """

    ambiguous_tasks = []

    # 🔥 helper checks
    def is_vague(text):
        text = text.lower()
        return any(word in text for word in [
            "everything", "stuff", "things", "something",
            "anything", "fix it", "handle it", "do it"
        ])

    def unclear_deadline(text):
        text = text.lower()
        return any(word in text for word in [
            "soon", "later", "asap", "quickly"
        ])

    for t in tasks:
        status = t.get("status", "")
        confidence = t.get("confidence", 1)
        owner = t.get("owner", "Unassigned")
        needs_flag = t.get("needs_clarification", False)
        task_text = t.get("task", "")

        # 🔥 Determine ambiguity
        is_ambiguous = (
            status in {"NEEDS_CLARIFICATION", "SUGGESTED"} or
            confidence < 0.5 or
            owner == "Unassigned" or
            needs_flag or
            is_vague(task_text) or
            unclear_deadline(task_text)
        )

        if is_ambiguous:

            reasons = []

            # 👤 Owner issues
            if owner == "Unassigned":
                reasons.append("Missing owner")

            # 📉 Confidence
            if confidence < 0.5:
                reasons.append("Low confidence")

            # 🧠 Vague task
            if is_vague(task_text):
                reasons.append("Vague task")

            # ⏰ Deadline unclear
            if unclear_deadline(task_text):
                reasons.append("Unclear deadline")

            # ⚠ Suggested
            if status == "SUGGESTED":
                reasons.append("Suggested assignment")

            # 🔥 fallback
            if not reasons:
                reasons.append("Needs attention")

            t["message"] = ", ".join(reasons)

            ambiguous_tasks.append(t)

    return ambiguous_tasks