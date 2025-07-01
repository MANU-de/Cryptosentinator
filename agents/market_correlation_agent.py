# agents/market_correlation_agent.py
from typing import List, Dict
from collections import defaultdict
from ..graph_state import GraphState, ProcessedDocument, MarketInsight # Relative import
from ..tools.market_data_tools import get_mock_crypto_price_data # Relative import

class MarketCorrelationAgent:
    def __init__(self):
        self.price_tool = get_mock_crypto_price_data

    def run(self, state: GraphState) -> dict:
        print("--- AGENT: Market Correlation Running ---")
       # print("Received processed_documents:", state.get("processed_documents"))
        print("Received keywords:", state.get("keywords"))
        processed_documents = state.get("processed_documents", [])
        # In a real system, you'd iterate through relevant cryptocurrencies
        # For this demo, let's assume we are interested in the keywords provided initially
        # Or a specific cryptocurrency passed in state, e.g., state.get("current_cryptocurrency")
        
        keywords_to_correlate = state.get("keywords", [])
        if not processed_documents or not keywords_to_correlate:
            return {"error_message": "No processed documents or keywords for correlation."}

        insights: List[MarketInsight] = []

        # Group documents by keyword (cryptocurrency)
        docs_by_keyword: Dict[str, List[ProcessedDocument]] = defaultdict(list)
        for doc_dict in processed_documents:
            doc = ProcessedDocument(**doc_dict) if isinstance(doc_dict, dict) else doc_dict
            docs_by_keyword[doc["keyword"]].append(doc)

        for keyword, docs in docs_by_keyword.items():
            if not docs:
                continue

            print(f"Correlating for: {keyword}")
            current_crypto_symbol = keyword # Assuming keyword is the crypto symbol

            # 1. Aggregate Sentiment
            valid_sentiments = [doc["sentiment_score"] for doc in docs if doc["sentiment_score"] is not None]
            overall_sentiment_score = sum(valid_sentiments) / len(valid_sentiments) if valid_sentiments else 0.0
            
            sentiment_trend = "Stable"
            if len(valid_sentiments) > 1:
                # Simplistic trend: compare first half avg to second half avg if sorted by time
                # For a real system, you'd need proper time-series analysis
                first_half_avg = sum(valid_sentiments[:len(valid_sentiments)//2]) / (len(valid_sentiments)//2) if len(valid_sentiments)//2 > 0 else 0
                second_half_avg = sum(valid_sentiments[len(valid_sentiments)//2:]) / (len(valid_sentiments) - len(valid_sentiments)//2) if (len(valid_sentiments) - len(valid_sentiments)//2) > 0 else 0
                if second_half_avg > first_half_avg + 0.1: sentiment_trend = "Improving"
                elif second_half_avg < first_half_avg - 0.1: sentiment_trend = "Declining"

            # 2. Get Market Data (Mock)
            try:
                price_data = self.price_tool.invoke({"cryptocurrency_symbol": current_crypto_symbol})
            except Exception as e:
                print(f"Could not fetch price data for {current_crypto_symbol}: {e}")
                price_data = {"price": "N/A", "24h_change_percent": "N/A"}


            # 3. Basic Correlation Logic (Example)
            correlation_notes = []
            if overall_sentiment_score > 0.5 and price_data.get("24h_change_percent", 0) > 2:
                correlation_notes.append(f"Strong positive sentiment ({overall_sentiment_score:.2f}) coincides with price increase ({price_data.get('24h_change_percent')}%). Potential bullish signal for {current_crypto_symbol}.")
            elif overall_sentiment_score < -0.3 and price_data.get("24h_change_percent", 0) < -2:
                correlation_notes.append(f"Strong negative sentiment ({overall_sentiment_score:.2f}) seen with price decrease ({price_data.get('24h_change_percent')}%). Potential bearish signal for {current_crypto_symbol}.")
            elif overall_sentiment_score > 0.3:
                 correlation_notes.append(f"Generally positive sentiment ({overall_sentiment_score:.2f}) for {current_crypto_symbol}. Market price: ${price_data.get('price')}, 24h change: {price_data.get('24h_change_percent')}%")
            else:
                correlation_notes.append(f"Neutral or mixed sentiment ({overall_sentiment_score:.2f}) for {current_crypto_symbol}. Market price: ${price_data.get('price')}, 24h change: {price_data.get('24h_change_percent')}%")

            # Get a few key articles/posts
            key_docs_info = []
            # Sort docs by sentiment score (absolute value to find strongest opinions)
            sorted_docs = sorted(docs, key=lambda d: abs(d.get("sentiment_score", 0) or 0), reverse=True)
            for doc in sorted_docs[:2]: # Top 2 most opinionated
                if doc.get("sentiment_score") is not None:
                     key_docs_info.append({"content": doc["content"][:100] + "...", "sentiment": doc["sentiment_score"]})


            insight = MarketInsight(
                cryptocurrency=current_crypto_symbol,
                overall_sentiment_score=round(overall_sentiment_score, 3),
                sentiment_trend=sentiment_trend,
                correlation_notes=correlation_notes,
                key_articles_or_posts=key_docs_info
            )
            insights.append(insight)
        
        print(f"Generated {len(insights)} market insights.")
        return {"market_insights": insights}

market_correlation_agent = MarketCorrelationAgent()