import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any
import hashlib
import os


class EnterpriseLogger:
    """Enterprise Logger with AI Insights + Business Impact"""

    def __init__(self, db_path="agent.db"):
        self.db_path = db_path
        self.session_id = self._generate_session_id()

        self._setup_logging()
        self._init_db()

    # ===============================
    # 🔹 LOGGING SETUP
    # ===============================
    def _setup_logging(self):
        self.logger = logging.getLogger("agent_logger")
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler("app.log")
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    # ===============================
    # 🔹 DB INIT
    # ===============================
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            level TEXT,
            message TEXT,
            component TEXT
        )
        """)

        conn.commit()
        conn.close()

    # ===============================
    # 🔹 GENERATE SESSION
    # ===============================
    def _generate_session_id(self):
        return hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]

    # ===============================
    # 🔥 BASIC LOGGING
    # ===============================
    def log(self, level: str, message: str, component="system"):

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO logs (timestamp, level, message, component)
        VALUES (?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            level,
            message,
            component
        ))

        conn.commit()
        conn.close()

        getattr(self.logger, level.lower(), self.logger.info)(message)

    # ===============================
    # 🔥 ERROR LOGGING
    # ===============================
    def log_error(self, error: str):
        self.log("ERROR", error, "system")

    # ===============================
    # 🔥 TASK EVENTS (IMPORTANT)
    # ===============================
    def log_task_event(self, task: Dict):

        message = f"Task processed: {task.get('task')} | Owner: {task.get('owner')}"
        self.log("INFO", message, "task")

    # ===============================
    # 🔥 PERFORMANCE METRICS
    # ===============================
    def log_metric(self, name: str, value: float):

        self.log("INFO", f"{name}: {value}", "metric")

    # ===============================
    # 🔥 AI INSIGHTS FROM LOGS
    # ===============================
    def generate_insights(self) -> List[str]:

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT level, message FROM logs ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()
        conn.close()

        insights = []

        errors = len([r for r in rows if r[0] == "ERROR"])
        total = len(rows)

        if errors > 5:
            insights.append("⚠ High error rate detected")

        if total > 0 and errors == 0:
            insights.append("✅ System running smoothly")

        if total > 20:
            insights.append("🚀 High system activity")

        return insights

    # ===============================
    # 🔥 BUSINESS IMPACT FROM LOGS
    # ===============================
def calculate_business_impact(tasks):

    if not tasks:
        return 0, 0, 0

    # ✅ ONLY confirmed + automated tasks
    confirmed_automated_tasks = [
        t for t in tasks 
        if t.get("status") == "CONFIRMED" and t.get("automated") == True
    ]

    total_confirmed_tasks = [
        t for t in tasks 
        if t.get("status") == "CONFIRMED"
    ]

    # ⏱️ Time saved
    time_saved = len(confirmed_automated_tasks) * 5

    # 💰 Cost saved
    cost_saved = time_saved * 0.5

    # 🤖 Automation %
    automation_percent = (
        (len(confirmed_automated_tasks) / len(total_confirmed_tasks)) * 100
        if len(total_confirmed_tasks) > 0 else 0
    )

    return time_saved, cost_saved, round(automation_percent, 2)

    # ===============================
    # 🔥 DASHBOARD OUTPUT
    # ===============================
    def get_dashboard(self):

        impact = self.calculate_business_impact()
        insights = self.generate_insights()

        return {
            "impact": impact,
            "insights": insights
        }


# GLOBAL INSTANCE
enterprise_logger = EnterpriseLogger()