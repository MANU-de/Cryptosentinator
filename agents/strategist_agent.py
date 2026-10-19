#gemini-3.1-flash-lite-preview

# agents/strategist_agent.py
from graph_state import GraphState, StrategicSummary
from tools.market_data_tools import get_mock_crypto_price_data
from tools.llm_client import generate_strategic_json

class StrategistAgent:
    """
    The Strategist Agent synthesizes multi-source intelligence using a
    model-agnostic LLM router (Gemini with Hugging Face Qwen 2.5 72B fallback).
    """
    def run(self, state: GraphState) -> dict:
        print("--- AGENT: Strategist (Model-Agnostic & Multi-Timeframe) ---")
        processed_documents = state["processed_documents"]
        keyword = state["keywords"][0]

        # 1. Summarize sentiment and identified narratives
        avg_sentiment = (
            sum(doc["sentiment_score"] for doc in processed_documents if doc.get("sentiment_score") is not None) / len(processed_documents)
            if processed_documents else 0.0
        )
        topics = [doc["topic"] for doc in processed_documents if doc.get("topic")]
        unique_topics = list(set(topics))
        topic_summary = ", ".join(unique_topics) if unique_topics else "General Market Trend"

        # 2. Baseline context
        market_data = get_mock_crypto_price_data.run({"cryptocurrency_symbol": keyword})
        price = market_data.get("price", "N/A")
        change = market_data.get("24h_change_percent", "N/A")

        # 3. Prepare structured snippets
        evidence_snippets = [
            f"[{doc.get('source', 'source')} | {doc.get('topic', 'Topic')}]: {doc['content'][:90]}... (Score: {doc.get('sentiment_score', 0):.2f})"
            for doc in processed_documents[:6]
        ]

        # 4. Prompt formulation
        prompt = f"""
You are an institutional crypto market strategist and risk manager.
Synthesize the multi-source intelligence below into a structured JSON analysis.

**Input Intelligence:**
- Target Asset: {keyword}
- Current Baseline Price: ${price} (24h Change: {change}%)
- Aggregate Sentiment Score: {avg_sentiment:.2f} (-1.0 Bearish to +1.0 Bullish)
- Active Market Narratives: {topic_summary}
- Multi-Source Evidence Snippets:
{chr(10).join(f"  * {snippet}" for snippet in evidence_snippets)}

**Your Task:**
Generate a JSON object with this exact structure:
{{
  "cryptocurrency": "{keyword}",
  "hypothesis": "[24h Tactical]: <momentum/volatility outlook>. [7d Strategic]: <on-chain & narrative trend>. [Invalidation Trigger]: <specific price action or funding condition that invalidates this view>.",
  "confidence": "High" or "Medium" or "Low",
  "reasoning": "<3-4 sentence institutional reasoning linking funding rate leverage, on-chain TVL, and retail sentiment>.",
  "supporting_evidence": ["<snippet 1>", "<snippet 2>", "<snippet 3>"]
}}
Respond ONLY with the JSON object.
"""

        summary_json = generate_strategic_json(prompt)

        required_keys = ["cryptocurrency", "hypothesis", "confidence", "reasoning", "supporting_evidence"]
        if summary_json and all(k in summary_json for k in required_keys):
            if not isinstance(summary_json["supporting_evidence"], list):
                summary_json["supporting_evidence"] = [str(summary_json["supporting_evidence"])]
            return {"strategic_summaries": [StrategicSummary(**summary_json)]}

        # Fallback if both LLM endpoints are unreachable
        print("Falling back to default strategic summary.")
        fallback = StrategicSummary(
            cryptocurrency=keyword,
            hypothesis=f"[24h Tactical]: Neutral consolidation. [7d Strategic]: Trend following market baseline. [Invalidation Trigger]: Break below 24h low.",
            confidence="Medium",
            reasoning="Sufficient multi-source alignment was unavailable to build a high-conviction outlook.",
            supporting_evidence=[f"Baseline Price: ${price}"]
        )
        return {"strategic_summaries": [fallback]}

strategist_agent = StrategistAgent()