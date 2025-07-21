
from ..graph_state import GraphState, PerformanceEvaluation
from ..tools.market_data_tools import get_mock_market_outcome

class EvaluatorAgent:
    """
    The Evaluator Agent assesses the Strategist's hypothesis against a
    simulated ground truth to score performance.
    """
    def run(self, state: GraphState) -> dict:
        print("--- AGENT: Evaluator ---")
        summary = state["strategic_summaries"][0]
        raw_documents = state["raw_documents"]

        # 1. Get the simulated "ground truth" outcome
        simulated_outcome = get_mock_market_outcome.invoke({"raw_documents": raw_documents})

        # 2. Evaluate the hypothesis against the outcome
        hypothesis = summary["hypothesis"].lower()
        outcome = simulated_outcome.lower()
        
        result = "Incorrect"
        notes = "The hypothesis did not match the simulated market outcome."

        is_bullish_hypothesis = "bullish" in hypothesis or "increase" in hypothesis or "positive" in hypothesis
        is_bearish_hypothesis = "bearish" in hypothesis or "decrease" in hypothesis or "negative" in hypothesis
        
        is_positive_outcome = "positive" in outcome
        is_negative_outcome = "negative" in outcome

        if (is_bullish_hypothesis and is_positive_outcome) or \
           (is_bearish_hypothesis and is_negative_outcome):
            result = "Correct"
            notes = "The hypothesis correctly predicted the direction of the simulated market movement."
        elif not is_bullish_hypothesis and not is_bearish_hypothesis and "stable" in outcome:
            result = "Correct"
            notes = "The neutral hypothesis correctly matched the stable simulated market."
        elif (is_bullish_hypothesis and "stable" in outcome) or (is_bearish_hypothesis and "stable" in outcome):
            result = "Partially Correct"
            notes = "The hypothesis predicted a strong move, but the market was stable."

        evaluation = PerformanceEvaluation(
            cryptocurrency=summary["cryptocurrency"],
            hypothesis_tested=summary["hypothesis"],
            simulated_outcome=simulated_outcome,
            evaluation_result=result,
            evaluation_notes=notes
        )
        
        return {"evaluation": evaluation}

evaluator_agent = EvaluatorAgent()