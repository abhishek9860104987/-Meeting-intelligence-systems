import json
import time
from datetime import datetime
from typing import Dict, Any
import re

from database import log_error, get_error_history


class SelfHealingAgent:
    """Advanced self-healing agent for autonomous task recovery"""

    def __init__(self):
        self.retry_patterns = {
            "api_failure": ["timeout", "connection", "rate limit", "503", "502"],
            "parsing_error": ["json", "parse", "malformed", "invalid"],
            "assignment_failure": ["unassigned", "ambiguous", "unclear"],
            "data_corruption": ["duplicate", "missing", "null", "empty"]
        }

    # ===============================
    # 🔥 MAIN ENTRY
    # ===============================
    def diagnose_and_heal(self, task_data: Dict, error_context: Dict):

        error_type = self._classify_error(error_context)

        if error_type == "api_failure":
            return self._heal_api_failure(task_data, error_context)

        elif error_type == "parsing_error":
            return self._heal_parsing_error(task_data)

        elif error_type == "assignment_failure":
            return self._heal_assignment_failure(task_data)

        elif error_type == "data_corruption":
            return self._heal_data(task_data)

        return self._default_healing(task_data, error_context)

    # ===============================
    # 🔍 ERROR CLASSIFICATION
    # ===============================
    def _classify_error(self, error_context):
        msg = str(error_context).lower()

        for etype, patterns in self.retry_patterns.items():
            if any(p in msg for p in patterns):
                return etype

        return "unknown"

    # ===============================
    # 🔥 API FAILURE RECOVERY
    # ===============================
    def _heal_api_failure(self, task_data, error_context):
        retry_count = error_context.get("retry_count", 0)

        if retry_count >= 3:
            return {
                "status": "fallback",
                "message": "Switched to fallback strategy",
                "data": task_data
            }

        wait = min(2 ** retry_count, 8)
        time.sleep(wait)

        return {
            "status": "retry",
            "retry_count": retry_count + 1,
            "wait_time": wait
        }

    # ===============================
    # 🔥 PARSING RECOVERY
    # ===============================
    def _heal_parsing_error(self, task_data):

        text = str(task_data)

        patterns = [
            r"(\w+)\s+(will|should|needs to)\s+(.+)",
            r"(?:task|action):\s*(.+)",
            r"(.+?)\s+(?:by|before|due)"
        ]

        for p in patterns:
            match = re.search(p, text, re.IGNORECASE)
            if match:
                return {
                    "status": "healed",
                    "data": {
                        "task": match.group(1) if match.groups() else text[:100],
                        "confidence": 0.6
                    }
                }

        return {
            "status": "manual",
            "message": "Parsing failed"
        }

    # ===============================
    # 🔥 ASSIGNMENT RECOVERY
    # ===============================
    def _heal_assignment_failure(self, task_data):

        return {
            "status": "healed",
            "data": {
                **task_data,
                "owner": "Auto-Assigned",
                "confidence": 0.7
            }
        }

    # ===============================
    # 🔥 DATA CLEANING
    # ===============================
    def _heal_data(self, task_data):

        if not isinstance(task_data, dict):
            return {"status": "failed"}

        cleaned = {}

        for k, v in task_data.items():
            if v and str(v).strip():
                cleaned[k] = str(v).strip()

        return {
            "status": "healed",
            "data": cleaned
        }

    # ===============================
    # 🔥 DEFAULT HANDLER
    # ===============================
    def _default_healing(self, task_data, error_context):

        log_error(str(error_context))

        return {
            "status": "escalated",
            "message": "Unknown error, escalated",
            "data": task_data
        }

    # ===============================
    # 🔥 SYSTEM HEALTH
    # ===============================
    def monitor_system_health(self):

        errors = get_error_history(hours=24)

        if len(errors) > 10:
            return {
                "health": "degraded",
                "error_count": len(errors),
                "insight": "⚠ System experiencing high failure rate"
            }

        return {
            "health": "healthy",
            "error_count": len(errors),
            "insight": "✅ System running smoothly"
        }

    # ===============================
    # 🔥 AI INSIGHTS (NEW 🔥)
    # ===============================
    def generate_healing_insights(self, result: Dict[str, Any]):

        insights = []

        status = result.get("status")

        if status == "retry":
            insights.append("🔁 System retrying automatically")

        elif status == "healed":
            insights.append("🛠 Issue auto-resolved")

        elif status == "fallback":
            insights.append("⚡ Fallback strategy activated")

        elif status == "manual":
            insights.append("👤 Manual intervention required")

        elif status == "escalated":
            insights.append("🚨 Escalated to system admin")

        return insights