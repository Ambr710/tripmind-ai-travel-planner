"""
tools.py
--------
"Tool Calling" layer of the Agentic AI system.

In a production system these would call real external APIs (e.g.
OpenWeatherMap for weather). To keep this project runnable without any
paid API key, WeatherTool uses a small deterministic seasonal model
based on month + destination, and clearly logs itself as a TOOL CALL so
the agentic behaviour remains visible in the console/screenshots.
"""

import datetime
import random


class WeatherTool:
    """Simulated weather lookup tool the agent can invoke."""

    SEASONAL_PROFILE = {
        "paris":   {"summer": (20, 26), "winter": (2, 8), "spring": (10, 18), "autumn": (9, 17)},
        "goa":     {"summer": (28, 34), "winter": (20, 30), "spring": (26, 33), "autumn": (25, 31)},
        "tokyo":   {"summer": (25, 31), "winter": (2, 10), "spring": (12, 20), "autumn": (14, 22)},
        "manali":  {"summer": (10, 25), "winter": (-5, 8), "spring": (8, 20),  "autumn": (5, 18)},
    }

    @staticmethod
    def _season_for_month(month: int) -> str:
        if month in (12, 1, 2):
            return "winter"
        if month in (3, 4, 5):
            return "spring"
        if month in (6, 7, 8):
            return "summer"
        return "autumn"

    def get_weather(self, destination: str, month: int = None) -> dict:
        month = month or datetime.date.today().month
        dest_key = destination.strip().lower()
        season = self._season_for_month(month)
        profile = self.SEASONAL_PROFILE.get(dest_key, {"summer": (20, 30), "winter": (5, 15),
                                                         "spring": (15, 25), "autumn": (12, 22)})
        low, high = profile[season]
        temp = round(random.uniform(low, high), 1)
        condition = random.choice(["Clear", "Partly Cloudy", "Light Rain", "Sunny", "Overcast"])
        print(f"  [TOOL CALL] WeatherTool.get_weather(destination='{destination}', month={month})")
        return {
            "destination": destination.title(),
            "month": month,
            "season": season,
            "expected_temp_c": temp,
            "condition": condition,
        }


class BudgetEstimatorTool:
    """Estimates a trip budget by combining category costs looked up
    from the RAG knowledge base with the number of days/travelers."""

    CATEGORY_SPLIT = {
        "budget": {"stay": 0.35, "food": 0.25, "transport": 0.20, "activities": 0.20},
        "mid-range": {"stay": 0.40, "food": 0.25, "transport": 0.15, "activities": 0.20},
        "luxury": {"stay": 0.50, "food": 0.20, "transport": 0.10, "activities": 0.20},
    }

    def estimate(self, daily_cost_usd: float, days: int, travelers: int,
                 tier: str = "mid-range") -> dict:
        print(f"  [TOOL CALL] BudgetEstimatorTool.estimate(daily_cost={daily_cost_usd}, "
              f"days={days}, travelers={travelers}, tier='{tier}')")
        total = daily_cost_usd * days * travelers
        split = self.CATEGORY_SPLIT.get(tier, self.CATEGORY_SPLIT["mid-range"])
        breakdown = {cat: round(total * pct, 2) for cat, pct in split.items()}
        return {
            "tier": tier,
            "days": days,
            "travelers": travelers,
            "estimated_total_usd": round(total, 2),
            "breakdown_usd": breakdown,
        }
