import json
import re
from utils.groq_client import call_groq


INVALID_NAMES = {
    "In", "On", "At", "By", "Of", "And", "Or", "But", "So",
    "Database", "System", "UI", "Backend", "Frontend"
}


# ===============================
# 🔥 NAME EXTRACTION
# ===============================
def extract_possible_names(text):
    candidates = re.findall(r"\b[A-Z][a-z]+\b", text)
    return list(set([c for c in candidates if c not in INVALID_NAMES]))


def is_valid_name(name):
    return name and name not in INVALID_NAMES


# ===============================
# 🔥 OWNER DETECTION (IMPROVED)
# ===============================
def detect_owner_from_sentence(sentence):

    # supports: "Abhishek will", "Rohit should", "Aman needs to"
    match = re.search(r"\b([A-Z][a-z]+)\s+(will|should|needs to)\b", sentence)

    if match:
        name = match.group(1)

        if is_valid_name(name) and name.lower() not in ["someone", "team"]:
            return name

    return None


# ===============================
# 🔥 VAGUE TASK CHECK
# ===============================
def is_vague_task(text):
    text = text.lower()
    vague_words = ["someone", "something", "anything", "everything", "team"]
    return any(w in text for w in vague_words)


# ===============================
# 🔥 STATUS FILTER
# ===============================
def is_status_statement(text):
    text = text.lower()
    return any(w in text for w in [
        "done", "complete", "completed", "working",
        "finished", "mostly", "is ready"
    ])


# ===============================
# 🔥 CLEAN TASK TEXT (IMPROVED)
# ===============================
def clean_task_text(text):
    text = re.sub(
        r"\b[A-Z][a-z]+\s+(will|should|needs to)\s+",
        "",
        text,
        flags=re.IGNORECASE
    )

    # remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    # capitalize first letter
    if text:
        text = text[0].upper() + text[1:]

    return text


# ===============================
# 🔥 NORMALIZE (FOR DUPLICATES)
# ===============================
def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9 ]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def remove_duplicates(tasks):
    seen = set()
    unique_tasks = []

    for t in tasks:
        norm = normalize_text(t["task"])
        if norm not in seen:
            seen.add(norm)
            unique_tasks.append(t)

    return unique_tasks


# ===============================
# 🔥 MAIN FUNCTION (FINAL)
# ===============================
def extract_tasks(transcript):

    if not transcript:
        return []

    lines = transcript.split("\n")
    tasks = []

    for line in lines:

        if not line.strip():
            continue

        text = line.strip()

        # ❌ Skip status updates
        if is_status_statement(text):
            continue

        # ===============================
        # 👤 OWNER DETECTION
        # ===============================
        owner = detect_owner_from_sentence(text)

        # ===============================
        # 🎯 CLEAN TASK
        # ===============================
        task_text = clean_task_text(text)

        # ===============================
        # 🧠 CONFIDENCE + STATUS
        # ===============================
        if is_vague_task(text):
            confidence = 0.3
            status = "NEEDS_CLARIFICATION"
            automated = False

        else:
            if owner:
                confidence = 0.9
                status = "AUTO_ASSIGNED"
                automated = True
            else:
                confidence = 0.6
                status = "SUGGESTED"
                automated = False

        # ===============================
        # 📦 TASK OBJECT
        # ===============================
        tasks.append({
            "task": task_text,
            "owner": owner if owner else "Unassigned",
            "deadline": "",
            "priority": "Medium",
            "confidence": round(confidence, 2),
            "status": status,
            "automated": automated,  # 🔥 CRITICAL FIELD
            "needs_clarification": status == "NEEDS_CLARIFICATION"
        })

    return remove_duplicates(tasks)