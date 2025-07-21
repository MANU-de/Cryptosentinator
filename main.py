import dotenv, os
dotenv.load_dotenv()

from .config import get_gemini_api_key
from langgraph.graph import StateGraph, END
from .graph_state import GraphState
from .agents.scout_agent import scout_agent
from .agents.intelligence_analyst_agent import intelligence_analyst_agent
from .agents.strategist_agent import strategist_agent
from .agents.evaluator_agent import evaluator_agent
import pprint

GEMINI_API_KEY = get_gemini_api_key()



def run_crypto_sentinator_v2(keywords: list[str]):
    """Initializes and runs the enhanced multi-agent system."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")

    workflow = StateGraph(GraphState)

    # Define the nodes with their new roles
    workflow.add_node("scout", scout_agent.run)
    workflow.add_node("analyst", intelligence_analyst_agent.run)
    workflow.add_node("strategist", strategist_agent.run)
    workflow.add_node("evaluator", evaluator_agent.run)

    # Define the new workflow
    workflow.set_entry_point("scout")
    workflow.add_edge("scout", "analyst")
    workflow.add_edge("analyst", "strategist")
    workflow.add_edge("strategist", "evaluator")
    workflow.add_edge("evaluator", END)

    app = workflow.compile()

    # Run the graph
    initial_state = {"keywords": keywords}
    print(f"\n🚀 Starting CryptoSentinator v2 for: {keywords} 🚀\n")
    
    final_state = app.invoke(initial_state)

    print("\n🏁 CryptoSentinator v2 Run Finished 🏁")
    print("\n--- Strategic Summary ---")
    if final_state.get("strategic_summaries"):
        pprint.pprint(final_state["strategic_summaries"][0], indent=2)
    
    print("\n--- Performance Evaluation ---")
    if final_state.get("evaluation"):
        pprint.pprint(final_state["evaluation"], indent=2)

    return final_state

if __name__ == "__main__":
    # Ensure you have a .env file 
    # Run from the parent directory: python -m your_project_folder.main
    target_keywords = ["Bitcoin"]
    results = run_crypto_sentinator_v2(target_keywords)
