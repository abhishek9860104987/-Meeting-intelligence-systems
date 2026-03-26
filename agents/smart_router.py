import time
from typing import Dict, List, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


# ===============================
# 🔹 MODEL TYPES
# ===============================
class ModelType(Enum):
    FAST = "fast"
    ACCURATE = "accurate"
    BALANCED = "balanced"


@dataclass
class ModelConfig:
    name: str
    model_type: ModelType
    cost_per_1k_tokens: float
    avg_response_time: float
    accuracy_score: float
    max_tokens: int


# ===============================
# 🔥 SMART ROUTER
# ===============================
class SmartRouter:

    def __init__(self):

        self.models = {
            "fast": ModelConfig("fast", ModelType.FAST, 0.05, 0.8, 0.85, 8000),
            "accurate": ModelConfig("accurate", ModelType.ACCURATE, 0.25, 2.5, 0.95, 8000),
            "balanced": ModelConfig("balanced", ModelType.BALANCED, 0.15, 1.5, 0.90, 16000)
        }

        self.usage = {k: {"calls": 0, "cost": 0.0} for k in self.models}

    # ===============================
    # 🔥 MAIN ROUTE FUNCTION
    # ===============================
    def route(self, task_type: str, prompt: str, priority="normal"):

        analysis = self._analyze(prompt, task_type)

        model = self._select_model(analysis, priority)

        cost = self._estimate_cost(model, prompt)

        decision = {
            "model": model,
            "reason": analysis,
            "cost": cost
        }

        return model, decision

    # ===============================
    # 🔍 ANALYZE REQUEST
    # ===============================
    def _analyze(self, prompt, task_type):

        length = len(prompt.split())

        complexity = 0
        if length > 100:
            complexity += 1
        if "analyze" in prompt.lower():
            complexity += 1

        return {
            "length": length,
            "complexity": complexity,
            "task_type": task_type
        }

    # ===============================
    # 🔥 MODEL SELECTION
    # ===============================
    def _select_model(self, analysis, priority):

        if priority == "high" or analysis["complexity"] >= 2:
            return "accurate"

        if analysis["length"] < 30:
            return "fast"

        return "balanced"

    # ===============================
    # 💰 COST ESTIMATION
    # ===============================
    def _estimate_cost(self, model, prompt):

        config = self.models[model]
        tokens = len(prompt.split()) * 1.3

        return (tokens / 1000) * config.cost_per_1k_tokens

    # ===============================
    # 🔥 RECORD USAGE
    # ===============================
    def record(self, model, cost):

        self.usage[model]["calls"] += 1
        self.usage[model]["cost"] += cost

    # ===============================
    # 💰 BUSINESS IMPACT
    # ===============================
    def calculate_impact(self):

        total_calls = sum(v["calls"] for v in self.usage.values())
        total_cost = sum(v["cost"] for v in self.usage.values())

        # Assume naive system would use expensive model always
        baseline_cost = total_calls * 0.25

        savings = baseline_cost - total_cost

        return {
            "calls": total_calls,
            "actual_cost": total_cost,
            "baseline_cost": baseline_cost,
            "savings": savings
        }

    # ===============================
    # 🧠 AI INSIGHTS
    # ===============================
    def generate_insights(self):

        impact = self.calculate_impact()
        insights = []

        if impact["savings"] > 1:
            insights.append("💰 Cost optimized using smart routing")

        if impact["calls"] > 10:
            insights.append("🚀 High system usage detected")

        if impact["actual_cost"] > impact["baseline_cost"]:
            insights.append("⚠ Costs higher than expected")

        return insights

    # ===============================
    # 📊 DASHBOARD OUTPUT
    # ===============================
    def get_dashboard(self):

        impact = self.calculate_impact()
        insights = self.generate_insights()

        return {
            "impact": impact,
            "insights": insights
        }


# GLOBAL INSTANCE
smart_router = SmartRouter()