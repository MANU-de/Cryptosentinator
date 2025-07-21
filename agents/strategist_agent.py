from langchain_core.tools import tool
from ..config import get_gemini_api_key
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParse
import google.generativeai as genai
from graph_state import GraphState, StrategicSummary
from tools.market_data_tools import get_mock_crypto_price_data
import json
import re


genai.configure(api_key=get_gemini_api_key())
model = genai.GenerativeModel('gemini-2.0-flash')

class StrategistAgent:
    """
    The Strategist Agent synthesizes processed data and market info to form a
    strategic hypothesis about market trends.
    """
    def run(self, state: GraphState) -> dict:
        print("--- AGENT: Strategist ---")
        processed_documents = state["processed_documents"]
        keyword = state["keywords"][0] # For simplicity, focus on the first keyword for the summary

        # 1. Summarize sentiment and topics
        avg_sentiment = sum(doc["sentiment_score"] for doc in processed_documents if doc["sentiment_score"] is not None) / len(processed_documents)
        topics = [doc["topic"] for doc in processed_documents if doc["topic"]]
        topic_summary = ", ".join(list(set(topics)))
        
        # 2. Get market context
        market_data = get_mock_crypto_price_data.invoke({"cryptocurrency_symbol": keyword})
        
        # 3. Use LLM to generate a strategic summary
        prompt = ChatPromptTemplate.from_template("""
        You are a crypto market strategist. Based on the provided data, formulate a strategic summary.

        **Input Data:**
        - Cryptocurrency: {keyword}
        - Average Sentiment Score: {avg_sentiment:.2f} (from -1 to 1)
        - Dominant Discussion Topics: {topic_summary}
        - Current Market Data: Price ${price}, 24h Change {change}%
        - Key Data Points (Evidence): {evidence}

        **Your Task:**
        Generate a JSON object with the following structure:
        - "cryptocurrency": The name of the crypto.
        - "hypothesis": A clear, one-sentence hypothesis about the potential market movement.
        - "confidence": Your confidence in this hypothesis ('High', 'Medium', or 'Low').
        - "reasoning": A 2-3 sentence explanation for your hypothesis, linking the sentiment, topics, and market data.
        - "supporting_evidence": A list of 2-3 key strings from the evidence that support your reasoning.
        
        Respond ONLY with the JSON object.
        """)
        
        evidence_snippets = [f"'{doc['content'][:70]}...' (Topic: {doc['topic']}, Sentiment: {doc['sentiment_score']:.2f})" for doc in processed_documents[:3]]

        chain = prompt | llm | JsonOutputParser()
        
        summary_json = chain.invoke({
            "keyword": keyword,
            "avg_sentiment": avg_sentiment,
            "topic_summary": topic_summary,
            "price": market_data.get("price"),
            "change": market_data.get("24h_change_percent"),
            "evidence": json.dumps(evidence_snippets)
        })

        return {"strategic_summaries": [StrategicSummary(**summary_json)]}

strategist_agent = StrategistAgent()