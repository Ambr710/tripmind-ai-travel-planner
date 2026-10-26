"""
agents.py
---------
Implements the Agentic AI layer: a Router (Orchestrator) Agent that
understands the user's natural-language request and decides which
specialised worker agent / tool should handle it (Multi-Agent
Collaboration), and the worker agents themselves:

    RouterAgent            -> classifies intent, dispatches the task
    ItineraryAgent          -> builds a personalised day-wise itinerary
    ComparisonAgent         -> compares two or more destinations
    BudgetAgent             -> estimates trip cost (uses BudgetEstimatorTool)
    WeatherAgent            -> fetches weather via WeatherTool
    QAAgent (Agentic RAG)   -> answers open questions using retrieved
                               chunks and always cites the source PDF

Each agent is intentionally small and single-purpose (the "Single
Agent" pattern), and RouterAgent composes them (the "Multi-Agent
Collaboration" pattern), exactly matching the objectives in the
project brief.
"""

import re
from tools import WeatherTool, BudgetEstimatorTool
from rag_engine import VectorStore

DESTINATIONS = ["paris", "goa", "tokyo", "manali"]

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}

# Rough baseline mid-range daily cost (USD) per destination, used by BudgetAgent
DAILY_COST_USD = {"paris": 180, "goa": 75, "tokyo": 190, "manali": 65}


def _find_destinations(text: str):
    text_l = text.lower()
    return [d for d in DESTINATIONS if d in text_l]


def _find_month(text: str):
    text_l = text.lower()
    for name, num in MONTHS.items():
        if name in text_l:
            return num
    return None


def _find_number(text: str, default=None):
    match = re.search(r"\b(\d+)\b", text)
    return int(match.group(1)) if match else default


class BaseAgent:
    name = "BaseAgent"

    def run(self, query: str, store: VectorStore):
        raise NotImplementedError


class ItineraryAgent(BaseAgent):
    name = "ItineraryAgent"

    def run(self, query: str, store: VectorStore):
        dests = _find_destinations(query) or ["goa"]
        dest = dests[0]
        days = _find_number(query, default=3)
        results = store.search(f"top attractions things to do in {dest}", top_k=2)

        attractions = []
        for r in results:
            # naive extraction of attraction-like lines from the retrieved chunk
            for line in r["text"].split("."):
                line = line.strip()
                if line and any(k in line.lower() for k in ["temple", "beach", "tower", "museum",
                                                              "fort", "market", "shrine", "valley",
                                                              "waterfall", "crossing", "pass"]):
                    attractions.append(line)
        attractions = attractions[:days + 2] or ["Explore the city center and local markets"]

        plan = [f"Personalized {days}-Day Itinerary for {dest.title()}\n"]
        for day in range(1, days + 1):
            spot = attractions[(day - 1) % len(attractions)]
            plan.append(f"  Day {day}: {spot}.")
        plan.append(f"\n  (Sources: {', '.join(sorted(set(r['source'] for r in results)))})")
        return "\n".join(plan)


class ComparisonAgent(BaseAgent):
    name = "ComparisonAgent"

    def run(self, query: str, store: VectorStore):
        dests = _find_destinations(query)
        if len(dests) < 2:
            return "Please mention at least two destinations to compare (e.g. 'compare Goa and Tokyo')."

        lines = [f"Comparison: {' vs '.join(d.title() for d in dests)}\n"]
        for dest in dests:
            budget_hits = store.search(f"estimated daily budget cost USD per day {dest}", top_k=4)
            weather_hits = store.search(f"best time to visit weather temperature {dest}", top_k=4)
            budget_hit = next((h for h in budget_hits if dest in h["source"] and "USD" in h["text"]), None)
            weather_hit = next((h for h in weather_hits if dest in h["source"]
                                 and ("Time to Visit" in h["text"] or "C." in h["text"] or " C " in h["text"])), None)
            lines.append(f"  {dest.title()}:")
            if budget_hit:
                lines.append(f"    Budget info -> {budget_hit['text'][:220]}...")
            if weather_hit:
                lines.append(f"    Weather info -> {weather_hit['text'][:220]}...")
        return "\n".join(lines)


class BudgetAgent(BaseAgent):
    name = "BudgetAgent"

    def __init__(self):
        self.tool = BudgetEstimatorTool()

    def run(self, query: str, store: VectorStore):
        dests = _find_destinations(query) or ["goa"]
        dest = dests[0]
        days = _find_number(query, default=5)
        travelers_match = re.search(r"(\d+)\s*(people|traveler|travellers|persons|pax)", query.lower())
        travelers = int(travelers_match.group(1)) if travelers_match else 1
        tier = "budget" if "budget" in query.lower() else (
            "luxury" if "luxury" in query.lower() else "mid-range")

        daily_cost = DAILY_COST_USD.get(dest, 100)
        result = self.tool.estimate(daily_cost, days, travelers, tier)
        breakdown_str = ", ".join(f"{k}: ${v}" for k, v in result["breakdown_usd"].items())
        return (f"Budget Estimate for {dest.title()} ({tier} tier, {days} days, {travelers} traveler(s)):\n"
                f"  Estimated Total: ${result['estimated_total_usd']}\n"
                f"  Breakdown -> {breakdown_str}")


class WeatherAgent(BaseAgent):
    name = "WeatherAgent"

    def __init__(self):
        self.tool = WeatherTool()

    def run(self, query: str, store: VectorStore):
        dests = _find_destinations(query) or ["goa"]
        dest = dests[0]
        month = _find_month(query)
        result = self.tool.get_weather(dest, month)
        return (f"Weather Forecast for {result['destination']} "
                f"(month #{result['month']}, {result['season']}):\n"
                f"  Expected Temperature: {result['expected_temp_c']} C, Condition: {result['condition']}")


class QAAgent(BaseAgent):
    """Agentic RAG: retrieves relevant chunks and synthesizes an answer,
    always attaching the source document for traceability."""
    name = "QAAgent"

    def run(self, query: str, store: VectorStore):
        results = store.search(query, top_k=3)
        if not results:
            return "I couldn't find relevant information in the travel guides for that question."
        lines = [f"Answer (Agentic RAG, top {len(results)} sources):\n"]
        for i, r in enumerate(results, 1):
            snippet = r["text"][:300].strip()
            lines.append(f"  [{i}] (source: {r['source']}, relevance: {r['score']}) {snippet}...")
        return "\n".join(lines)


class RouterAgent:
    """Decides which specialised agent should handle the incoming
    natural-language request. This is the 'brain' of the Agent
    Workflow described in the project objectives."""
    name = "RouterAgent"

    def __init__(self, store: VectorStore):
        self.store = store
        self.agents = {
            "itinerary": ItineraryAgent(),
            "comparison": ComparisonAgent(),
            "budget": BudgetAgent(),
            "weather": WeatherAgent(),
            "qa": QAAgent(),
        }

    def classify_intent(self, query: str) -> str:
        q = query.lower()
        if "compare" in q or " vs " in q or "versus" in q:
            return "comparison"
        if "budget" in q or "cost" in q or "estimate" in q or "$" in q:
            return "budget"
        if "weather" in q or "temperature" in q or "climate" in q:
            return "weather"
        if "itinerary" in q or "plan a trip" in q or "days in" in q or "day trip" in q:
            return "itinerary"
        return "qa"

    def handle(self, query: str) -> dict:
        intent = self.classify_intent(query)
        agent = self.agents[intent]
        print(f"[RouterAgent] Query: \"{query}\"")
        print(f"[RouterAgent] -> routed to: {agent.name} (intent='{intent}')")
        answer = agent.run(query, self.store)
        return {"intent": intent, "agent": agent.name, "answer": answer}
