def generate_questions(task):
    """
    Generate clarification questions for ambiguous tasks
    """

    task_text = task.get("task", "").lower()
    questions = []

    # 🔥 Vague task
    if any(word in task_text for word in [
        "everything", "stuff", "things", "something",
        "anything", "fix it", "handle it", "do it"
    ]):
        questions.append("What exactly needs to be done?")
        questions.append("Can you specify the scope of this task?")

    # 🔥 Missing owner
    if task.get("owner") == "Unassigned":
        questions.append("Who will be responsible for this task?")

    # 🔥 Unclear deadline
    if any(word in task_text for word in [
        "soon", "later", "asap", "quickly"
    ]):
        questions.append("What is the exact deadline?")

    # 🔥 Low confidence
    if task.get("confidence", 1) < 0.5:
        questions.append("Can you clarify the details of this task?")

    # 🔥 Default fallback
    if not questions:
        questions.append("Can you provide more details about this task?")

    return questions