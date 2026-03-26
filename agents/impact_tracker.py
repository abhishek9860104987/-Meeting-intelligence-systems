import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


# ===============================
# ENUMS
# ===============================
class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"


class KpiCategory(Enum):
    PRODUCTIVITY = "productivity"
    EFFICIENCY = "efficiency"
    COST = "cost"
    TIME = "time"


# ===============================
# DATA CLASSES
# ===============================
@dataclass
class MetricDefinition:
    name: str
    metric_type: MetricType
    category: KpiCategory
    unit: str
    description: str
    target_value: Optional[float] = None
    is_kpi: bool = False


# ===============================
# MAIN CLASS
# ===============================
class ImpactTracker:

    def __init__(self, db_path: str = "agent.db"):
        self.db_path = db_path
        self._init_db()

    # ===============================
    # DB INIT
    # ===============================
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS impact_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric TEXT,
            value REAL,
            timestamp TEXT
        )
        """)

        conn.commit()
        conn.close()

    # ===============================
    # RECORD METRIC
    # ===============================
    def record(self, metric: str, value: float):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO impact_logs (metric, value, timestamp)
        VALUES (?, ?, ?)
        """, (metric, value, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    # ===============================
    # 🔥 FIXED BUSINESS METRICS
    # ===============================
    def calculate_simple_metrics(self, tasks: List[Dict]) -> Dict[str, Any]:

        if not tasks:
            return {
                "total_tasks": 0,
                "confirmed": 0,
                "automated": 0,
                "time_saved": 0,
                "cost_saved": 0,
                "automation_rate": 0
            }

        # ✅ ONLY CONFIRMED TASKS
        confirmed_tasks = [
            t for t in tasks if t.get("status") == "CONFIRMED"
        ]

        # ✅ CONFIRMED + AUTOMATED
        confirmed_automated = [
            t for t in confirmed_tasks
            if t.get("automated") == True or t.get("automated") == 1
        ]

        total = len(tasks)
        confirmed = len(confirmed_tasks)
        automated = len(confirmed_automated)

        # ⏱ Time saved (5 min per task)
        time_saved = automated * 5

        # 💰 Cost saved (₹0.5 per min)
        cost_saved = time_saved * 0.5

        # 🤖 Automation rate (only confirmed)
        automation_rate = (
            (automated / confirmed) * 100 if confirmed > 0 else 0
        )

        # 🔥 STORE METRICS
        self.record("time_saved", time_saved)
        self.record("cost_saved", cost_saved)
        self.record("automation_rate", automation_rate)

        return {
            "total_tasks": total,
            "confirmed": confirmed,
            "automated": automated,
            "time_saved": time_saved,
            "cost_saved": cost_saved,
            "automation_rate": automation_rate
        }

    # ===============================
    # 🔥 AI INSIGHTS GENERATOR
    # ===============================
    def generate_ai_insights(self, metrics: Dict[str, Any]) -> List[str]:

        insights = []

        if metrics["automation_rate"] > 70:
            insights.append("🚀 High automation efficiency")
        else:
            insights.append("⚡ Automation can be improved")

        if metrics["cost_saved"] > 1000:
            insights.append("💰 Significant cost savings achieved")

        if metrics["automated"] < metrics["confirmed"]:
            insights.append("⚠ Some confirmed tasks are still manual")

        if metrics["time_saved"] > 50:
            insights.append("⏱ Strong productivity gain")

        return insights

    # ===============================
    # 🔥 DASHBOARD
    # ===============================
    def get_dashboard(self, tasks: List[Dict]) -> Dict[str, Any]:

        metrics = self.calculate_simple_metrics(tasks)
        insights = self.generate_ai_insights(metrics)

        return {
            "metrics": metrics,
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }


# GLOBAL INSTANCE
impact_tracker = ImpactTracker()