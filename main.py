"""
main.py
-------
AI Smart Travel Planning Assistant - Entry point.

Demonstrates:
  - Loading travel guide PDFs and building a vector database (RAG)
  - An Agent Workflow (RouterAgent) that determines the appropriate
    action / worker agent for each user request (Agentic AI)
  - Multi-Agent Collaboration between Itinerary, Comparison, Budget,
    Weather and QA agents
  - Tool Calling (WeatherTool, BudgetEstimatorTool)
  - Agentic RAG with source-document references

Usage:
    python src/main.py                 # runs the built-in demo queries
    python src/main.py --interactive   # chat loop
"""

import os
import sys
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_engine import VectorStore
from agents import RouterAgent


PDF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pdfs")

DEMO_QUERIES = [
    "Plan a 4 day itinerary for Goa",
    "Compare Paris and Tokyo",
    "Estimate a budget trip to Manali for 5 days for 2 people",
    "What is the weather like in Tokyo in April?",
    "What documents do I need before traveling to Paris?",
    "Recommend tourist attractions near Old Manali",
]


def build_store():
    print("=" * 70)
    print("Loading travel guide PDFs and building the vector database (RAG)...")
    store = VectorStore().load_pdfs(PDF_DIR)
    print(f"Indexed {len(store.chunks)} text chunks from "
          f"{len(set(c.source for c in store.chunks))} documents.")
    print("=" * 70)
    return store


def run_demo(store):
    router = RouterAgent(store)
    for q in DEMO_QUERIES:
        print("\n" + "-" * 70)
        result = router.handle(q)
        print(f"\n{result['answer']}\n")


def run_interactive(store):
    router = RouterAgent(store)
    print("\nAI Smart Travel Planning Assistant (type 'exit' to quit)")
    while True:
        try:
            q = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q or q.lower() in ("exit", "quit"):
            break
        print("-" * 70)
        result = router.handle(q)
        print(f"\nAssistant:\n{result['answer']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Smart Travel Planning Assistant")
    parser.add_argument("--interactive", action="store_true", help="Run an interactive chat loop")
    args = parser.parse_args()

    vector_store = build_store()
    if args.interactive:
        run_interactive(vector_store)
    else:
        run_demo(vector_store)
