from langchain_core.tools import tool
from ..config import get_gemini_api_key
from langchain_core.prompts import ChatPromptTemplate
import google.generativeai as genai
from ..graph_state import GraphState, StrategicSummary
from ..tools.market_data_tools import get_mock_crypto_price_data
import json
import re


genai.configure(api_key=get_gemini_api_key())
model = genai.GenerativeModel('gemini-2.0-flash')

def extract_json_from_response(response_text: str) -> dict:
    """Extracts the first JSON object found in a string."""
    try:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {}
    except Exception as e:
        print(f"Error extracting JSON: {e}")
        return {}

class StrategistAgent:
    """
    The Strategist Agent synthesizes processed data and market info to form a
    strategic hypothesis about market trends.
    """
    def run(self, state: GraphState) -> dict:
        print("--- AGENT: Strategist ---")
        processed_documents = state["processed_documents"]
        keyword = state["keywords"][0]  # For simplicity, focus on the first keyword for the summary

        # 1. Summarize sentiment and topics
        avg_sentiment = (
            sum(doc["sentiment_score"] for doc in processed_documents if doc["sentiment_score"] is not None) / len(processed_documents)
            if processed_documents else 0.0
        )
        topics = [doc["topic"] for doc in processed_documents if doc.get("topic")]
        topic_summary = ", ".join(list(set(topics)))

        # 2. Get market context
        market_data = get_mock_crypto_price_data({"cryptocurrency_symbol": keyword})
        price = market_data.get("price")
        change = market_data.get("24h_change_percent")

        # 3. Prepare evidence
        evidence_snippets = [
            f"'{doc['content'][:70]}...' (Topic: {doc.get('topic')}, Sentiment: {doc.get('sentiment_score', 0):.2f})"
            for doc in processed_documents[:3]
        ]

        # 4. Use Gemini to generate a strategic summary
        prompt = (
            "You are a crypto market strategist. Based on the provided data, formulate a strategic summary.\n\n"
            "**Input Data:**\n"
            f"- Cryptocurrency: {keyword}\n"
            f"- Average Sentiment Score: {avg_sentiment:.2f} (from -1 to 1)\n"
            f"- Dominant Discussion Topics: {topic_summary}\n"
            f"- Current Market Data: Price ${price}, 24h Change {change}%\n"
            f"- Key Data Points (Evidence): {evidence_snippets}\n\n"
            "**Your Task:**\n"
            "Generate a JSON object with the following structure:\n"
            '- "cryptocurrency": The name of the crypto.\n'
            '- "hypothesis": A clear, one-sentence hypothesis about the potential market movement.\n'
            '- "confidence": Your confidence in this hypothesis (\'High\', \'Medium\', or \'Low\').\n'
            '- "reasoning": A 2-3 sentence explanation for your hypothesis, linking the sentiment, topics, and market data.\n'
            '- "supporting_evidence": A list of 2-3 key strings from the evidence that support your reasoning.\n\n'
            "Respond ONLY with the JSON object."
        )

        try:
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            summary_json = extract_json_from_response(response_text)
            # Basic validation
            required_keys = ["cryptocurrency", "hypothesis", "confidence", "reasoning", "supporting_evidence"]
            if not all(k in summary_json for k in required_keys):
                raise ValueError("Gemini response missing required keys.")
            if not isinstance(summary_json["supporting_evidence"], list):
                summary_json["supporting_evidence"] = [str(summary_json["supporting_evidence"])]
            return {"strategic_summaries": [StrategicSummary(**summary_json)]}
        except Exception as e:
            print(f"Error in strategist agent: {e}. Returning empty summary.")
            return {"strategic_summaries": []}

strategist_agent = StrategistAgent()