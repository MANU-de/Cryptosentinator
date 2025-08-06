import dotenv, os
dotenv.load_dotenv()

#from .config import get_gemini_api_key
from langgraph.graph import StateGraph, END
from graph_state import GraphState
from agents.scout_agent import scout_agent
from agents.intelligence_analyst_agent import intelligence_analyst_agent
from agents.strategist_agent import strategist_agent
from agents.evaluator_agent import evaluator_agent
import pprint

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") #or get_gemini_api_key()



#def run_crypto_sentinator_v2(keywords: list[str]):
    #"""Initializes and runs the enhanced multi-agent system."""
def create_interactive_pipeline(keywords_string: str) -> str:
    """
    Takes a comma-separated string of keywords, runs the full analysis pipeline,
    and returns a formatted Markdown string of the results.
    """
    print(f"Received keywords for analysis: {keywords_string}")
    if not GEMINI_API_KEY:
        #raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
        return "## Error: `OPENAI_API_KEY` is not set.\nPlease configure it in your environment or secrets."
    
    if not keywords_string or not keywords_string.strip():
        return "## Warning: No keywords provided.\nPlease enter at least one keyword to start the analysis."

    target_keywords = [keyword.strip() for keyword in keywords_string.split(',')]

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
    #initial_state = {"keywords": keywords}
    #print(f"\n🚀 Starting CryptoSentinator v2 for: {keywords} 🚀\n")
    # 2. Run the graph with the user's keywords
    initial_state = {"keywords": target_keywords}
    
    #final_state = app.invoke(initial_state)
    try:
        final_state = app.invoke(initial_state)
    except Exception as e:
        print(f"An error occurred during graph execution: {e}")
        return f"## Analysis Failed\nAn unexpected error occurred during the analysis. Please check the logs.\n\n**Error details:**\n```\n{e}\n```"

    #print("\n🏁 CryptoSentinator v2 Run Finished 🏁")
    #print("\n--- Strategic Summary ---")
    #if final_state.get("strategic_summaries"):
        #pprint.pprint(final_state["strategic_summaries"][0], indent=2)
    
    #print("\n--- Performance Evaluation ---")
    #if final_state.get("evaluation"):
        #pprint.pprint(final_state["evaluation"], indent=2)

    #return final_state

#if __name__ == "__main__":
    # Ensure you have a .env file 
    # Run from the parent directory: python -m your_project_folder.main
    #target_keywords = ["Bitcoin"]
    #results = run_crypto_sentinator_v2(target_keywords)
    if not final_state or not final_state.get("strategic_summaries"):
        return "## Analysis Complete\nNo strategic summary could be generated. This might be due to a lack of data for the provided keywords."

    summary = final_state["strategic_summaries"][0]
    evaluation = final_state.get("evaluation", {})

    report = f"""
    # 📊 Analysis Report for: {summary.get('cryptocurrency', 'N/A')}

    ## 🧠 Strategic Hypothesis
    - **Hypothesis:** {summary.get('hypothesis', 'N/A')}
    - **Confidence:** `{summary.get('confidence', 'N/A')}`
    - **Reasoning:** {summary.get('reasoning', 'N/A')}

    ---

    ## 🎯 Performance Evaluation (Simulation)
    - **Hypothesis Tested:** *"{evaluation.get('hypothesis_tested', 'N/A')}"*
    - **Simulated Market Outcome:** `{evaluation.get('simulated_outcome', 'N/A')}`
    - **Result:** **{evaluation.get('evaluation_result', 'N/A')}**
    - **Notes:** {evaluation.get('evaluation_notes', 'N/A')}

    ---

    ## 📜 Supporting Evidence
    """
    evidence_list = summary.get("supporting_evidence", [])
    if evidence_list:
        for item in evidence_list:
            report += f"- `{item}`\n"
    else:
        report += "- No specific evidence snippets were extracted.\n"
        
    return report
