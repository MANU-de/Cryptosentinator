
import os
import json
import re
from datetime import datetime, timezone
from graph_state import GraphState, PerformanceEvaluation
from tools.market_data_tools import get_mock_market_outcome
from tools.market_tools import fetch_binance_derivatives_data

HISTORY_FILE = "backtest_history.jsonl"

class EvaluatorAgent:
    """
    Supercharged Evaluator Agent:
    - Benchmarks hypotheses against both simulated scenarios and live 24h market data.
    - Persistently logs all evaluations to backtest_history.jsonl.
    - Computes rolling cumulative performance metrics (Win Rate, Total Logged Runs).
    """

    def _normalize_symbol(self, keyword: str) -> str:
        mapping = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL"}
        return mapping.get(keyword.lower().strip(), keyword.upper())

    def _load_history(self) -> list[dict]:
        """Loads historical backtest records."""
        records = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            records.append(json.loads(line))
            except Exception as e:
                print(f"Warning loading history: {e}")
        return records

    def _save_record(self, record: dict):
        """Appends a new evaluation record to persistent storage."""
        try:
            with open(HISTORY_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            print(f"Warning saving backtest record: {e}")

    def run(self, state: GraphState) -> dict:
        print("--- AGENT: Evaluator (Persistent Backtesting) ---")
        summary = state["strategic_summaries"][0]
        raw_documents = state["raw_documents"]
        crypto_symbol = self._normalize_symbol(summary["cryptocurrency"])

        # 1. Get Simulated Ground Truth
        simulated_outcome = get_mock_market_outcome.run({"raw_documents": raw_documents})

        # 2. Get Live Market Reality (Binance)
        live_market_data = fetch_binance_derivatives_data(crypto_symbol)
        live_change_pct = live_market_data.get("price_change_pct_24h", None)

        # 3. Timeframe-Aware Directional Parsing
        hypothesis_raw = summary["hypothesis"]
        hypothesis_lower = hypothesis_raw.lower()
        outcome_lower = simulated_outcome.lower()

        # Isolate [24h Tactical] if present, otherwise evaluate full text
        tactical_match = re.search(r'\[24h tactical\]:?(.*?)(?:\[|$)', hypothesis_lower)
        tactical_segment = tactical_match.group(1) if tactical_match else hypothesis_lower

        is_bullish = any(w in tactical_segment for w in ["bullish", "increase", "positive", "upside", "rally"])
        is_bearish = any(w in tactical_segment for w in ["bearish", "decrease", "negative", "downside", "drop"])
        is_consolidation = any(w in tactical_segment for w in ["consolidation", "range-bound", "neutral", "stable", "flat"])

        is_positive_outcome = "positive" in outcome_lower
        is_negative_outcome = "negative" in outcome_lower
        is_stable_outcome = "stable" in outcome_lower

        # 4. Evaluation Scoring
        result = "Incorrect"
        notes = "The hypothesis did not match the market outcome."

        if (is_bullish and is_positive_outcome) or (is_bearish and is_negative_outcome):
            result = "Correct"
            notes = "The tactical hypothesis accurately predicted market direction."
        elif is_consolidation and is_stable_outcome:
            result = "Correct"
            notes = "The range-bound / consolidation hypothesis correctly anticipated market stability."
        elif (is_bullish or is_bearish) and is_stable_outcome:
            result = "Partially Correct"
            notes = "The hypothesis anticipated directional volatility, but price held within a stable range."
        elif is_consolidation and (is_positive_outcome or is_negative_outcome):
            result = "Partially Correct"
            notes = "Expected consolidation, but market experienced directional movement."

        score_value = 1.0 if result == "Correct" else (0.5 if result == "Partially Correct" else 0.0)

        # 5. Persistent Record Logging
        new_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cryptocurrency": summary["cryptocurrency"],
            "confidence": summary.get("confidence", "Medium"),
            "hypothesis": hypothesis_raw,
            "simulated_outcome": simulated_outcome,
            "live_24h_change_pct": live_change_pct,
            "evaluation_result": result,
            "score": score_value
        }
        self._save_record(new_record)

        # 6. Compute Rolling Backtest Metrics
        history = self._load_history()
        total_runs = len(history)
        correct_count = sum(1 for r in history if r.get("evaluation_result") == "Correct")
        partial_count = sum(1 for r in history if r.get("evaluation_result") == "Partially Correct")
        cumulative_score = sum(r.get("score", 0.0) for r in history)
        win_rate = (cumulative_score / total_runs * 100) if total_runs > 0 else 0.0

        live_str = f"{live_change_pct:+.2f}%" if live_change_pct is not None else "N/A"
        enriched_notes = (
            f"{notes} "
            f"[Backtest Track Record: {win_rate:.1f}% Win Rate across {total_runs} runs "
            f"(Correct: {correct_count}, Partial: {partial_count}) | Live 24h Price Move: {live_str}]"
        )

        evaluation = PerformanceEvaluation(
            cryptocurrency=summary["cryptocurrency"],
            hypothesis_tested=hypothesis_raw,
            simulated_outcome=simulated_outcome,
            evaluation_result=result,
            evaluation_notes=enriched_notes
        )

        return {"evaluation": evaluation}

evaluator_agent = EvaluatorAgent()