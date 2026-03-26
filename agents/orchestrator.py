import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

# 🔥 IMPORT YOUR AGENTS
from agents.extractor import extract_tasks
from agents.ownership import process_ownership
from agents.ambiguity import get_ambiguous
from agents.tracker import track_time
from agents.summary import generate_summary
from agents.stall_detector import detect_stalls
from agents.escalation import escalate_tasks
from agents.notifier import send_notifications
from agents.impact_tracker import impact_tracker


# ===============================
# 🔹 AGENT TYPES
# ===============================
class AgentType(Enum):
    EXTRACTOR = "extractor"
    OWNERSHIP = "ownership"
    AMBIGUITY = "ambiguity"
    TRACKER = "tracker"
    SUMMARY = "summary"
    SELF_HEALING = "self_healing"
    DECISION = "decision"
    METRICS = "metrics"


# ===============================
# 🔹 MESSAGE STRUCTURE
# ===============================
@dataclass
class AgentMessage:
    sender: AgentType
    receiver: AgentType
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: str


# ===============================
# 🔹 FINAL ORCHESTRATOR
# ===============================
class AgentOrchestrator:

    def __init__(self):
        self.active_workflows = {}

    # ===============================
    # 🔥 MAIN PIPELINE (IMPORTANT)
    # ===============================
    async def run_full_system(self, transcript: str, project_name: str):

        workflow_id = f"wf_{int(datetime.now().timestamp())}"

        self.active_workflows[workflow_id] = {
            "status": "running",
            "start_time": datetime.now(),
            "history": []
        }

        try:
            # ===============================
            # 1. EXTRACT TASKS
            # ===============================
            tasks = extract_tasks(transcript)
            self._log(workflow_id, "extractor", "success")

            # ===============================
            # 2. ASSIGN OWNERS
            # ===============================
            tasks = process_ownership(tasks, project_name)
            self._log(workflow_id, "ownership", "success")

            # ===============================
            # 3. AMBIGUITY DETECTION
            # ===============================
            ambiguous = get_ambiguous(tasks)
            self._log(workflow_id, "ambiguity", "success")

            # ===============================
            # 4. TRACK TIME
            # ===============================
            tasks = track_time(tasks)
            self._log(workflow_id, "tracker", "success")

            # ===============================
            # 5. STALL DETECTION
            # ===============================
            stalled = detect_stalls()
            self._log(workflow_id, "stall_detector", "success")

            # ===============================
            # 6. ESCALATION
            # ===============================
            escalated = escalate_tasks(stalled)
            self._log(workflow_id, "escalation", "success")

            # ===============================
            # 7. NOTIFICATIONS
            # ===============================
            notifications = send_notifications(escalated, stalled)
            self._log(workflow_id, "notifier", "success")

            # ===============================
            # 8. BUSINESS IMPACT
            # ===============================
            dashboard = impact_tracker.get_dashboard(tasks)
            self._log(workflow_id, "impact_tracker", "success")

            # ===============================
            # 9. SUMMARY
            # ===============================
            summary = generate_summary(tasks)
            self._log(workflow_id, "summary", "success")

            # ===============================
            # 🔥 FINAL RESULT
            # ===============================
            result = {
                "tasks": tasks,
                "ambiguous_tasks": ambiguous,
                "stalled_tasks": stalled,
                "notifications": notifications,
                "business_metrics": dashboard["metrics"],
                "ai_insights": dashboard["insights"],
                "summary": summary
            }

            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["end_time"] = datetime.now()

            return result

        except Exception as e:
            self.active_workflows[workflow_id]["status"] = "failed"
            self.active_workflows[workflow_id]["error"] = str(e)
            raise

    # ===============================
    # 🔹 LOGGING
    # ===============================
    def _log(self, workflow_id, agent, status):
        self.active_workflows[workflow_id]["history"].append({
            "agent": agent,
            "status": status,
            "time": str(datetime.now())
        })

    # ===============================
    # 🔹 STATUS
    # ===============================
    def get_status(self, workflow_id):
        return self.active_workflows.get(workflow_id, {})