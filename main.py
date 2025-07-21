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
# print(os.environ.get("GEMINI_API_KEY"))
# print("GEMINI_API_KEY loaded:", GEMINI_API_KEY)  # Debug: Should print your key or None

'''def run_sentiment_analysis_system(keywords: list[str]):
    """
    Initializes and runs the multi-agent sentiment analysis system.
    """
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not found. Please set it in your .env file or config.py.")
        return

    # Initialize the graph
    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("data_harvester", data_harvester_agent.run)
    workflow.add_node("nlp_processor", nlp_processing_agent.run)
    workflow.add_node("market_correlator", market_correlation_agent.run)

    # Define the edges (the flow of work)
    workflow.set_entry_point("data_harvester")
    workflow.add_edge("data_harvester", "nlp_processor")
    workflow.add_edge("nlp_processor", "market_correlator")
    workflow.add_edge("market_correlator", END)

    # Compile the graph
    app = workflow.compile()

    # Run the graph
    initial_state = {
        "keywords": keywords,  # Must be a non-empty list
        "raw_documents": [],
        "processed_documents": [],
        "market_insights": []
    }
    
    print(f"\n🚀 Starting CryptoSentinator for keywords: {keywords} 🚀\n")
    
    final_state = None
    # LangGraph can stream events, here we just get the final state
    for s in app.stream(initial_state, {"recursion_limit": 50}):
        print(f"\n--- Current State after node: {list(s.keys())[0]} ---")
        pprint.pprint(s)
        if END in s: # Check if the graph has finished
            final_state = s[END]
            break
        # If not END, the key is the node name, and value is its output (updates to state)
        # The app automatically merges this into the main state for the next node.

    
    print("\n🏁 CryptoSentinator Run Finished 🏁")
    if final_state:
        print("\n--- Final Market Insights ---")
        if final_state.get("market_insights"):
            for insight in final_state["market_insights"]:
                pprint.pprint(insight, indent=2)
        elif final_state.get("error_message"):
            print(f"An error occurred: {final_state['error_message']}")
        else:
            print("No market insights generated or an unknown issue occurred.")
    else:
        print("The graph did not complete successfully or did not reach the END state.")

    return final_state


if __name__ == "__main__":
    # Example usage:
    # Create a .env file in the cryptosentinator directory with your GEMINI_API_KEY
    # Example .env content:
    # GEMINI_API_KEY="sk-your-gemini-api-key"
    
    # To run from the parent directory of cryptosentinator:
    # python -m cryptosentinator.main
    
    # For this structure, you'd typically run this from the directory *above* cryptosentinator
    # like: python -m cryptosentinator.main
    # If you are in the cryptosentinator directory itself, you might need to adjust imports
    # or run `python main.py` and change relative imports to `from .module import X` to `from module import X`
    # For simplicity, let's assume we are running this script directly for now and adjust if needed
    # by creating a runner script outside or using `python -m`
    
    # Test run:
    target_keywords = ["Bitcoin", "Ethereum"]  # Example keywords
    # To run from inside the 'cryptosentinator' directory (adjusting imports):
    # Change relative imports e.g. from .graph_state import GraphState to from graph_state import GraphState
    # For now, let's assume you'll run with `python -m cryptosentinator.main` from parent dir.
    results = run_sentiment_analysis_system(target_keywords)
    
    # If you want to print the full final state:
    if results:
        print("\n--- Full Final State ---")
        pprint.pprint(results, indent=2) '''
        


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
    # Ensure you have a .env file with OPENAI_API_KEY="sk-..."
    # Run from the parent directory: python -m your_project_folder.main
    target_keywords = ["Bitcoin"]
    results = run_crypto_sentinator_v2(target_keywords)
