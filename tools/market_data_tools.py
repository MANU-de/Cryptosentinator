
import random
from langchain_core.tools import tool

from ..graph_state import RawDocument
from typing import List, Dict

    
@tool
def get_mock_crypto_price_data(cryptocurrency_symbol: str) -> Dict:
    """Simulates fetching current cryptocurrency price data."""
    
    print(f"--- TOOL: Mock Crypto Price for '{cryptocurrency_symbol}' ---")
    price = random.uniform(1000, 60000)
    change = random.uniform(-5, 5)
    return {
        "symbol": cryptocurrency_symbol,
        "price": round(price, 2),
        "24h_change_percent": round(change, 2)
    }

@tool
def get_mock_market_outcome(raw_documents: List[RawDocument]) -> str:
    """
    Simulates a realistic market outcome 24 hours later based on the
    overall sentiment of the initial raw documents. This serves as the 'ground truth'
    for our evaluation agent.
    """
    print("--- TOOL: Simulating Market Outcome (Ground Truth) ---")
    if not raw_documents:
        return "Indeterminate market movement due to lack of data."

    # A simple way to create a consistent "ground truth":
    # The real outcome is likely influenced by the real sentiment.
    # We will simulate this by linking the outcome to the mock data content.
    positive_indicators = ['great news', 'moon', 'bullish', 'future', '🚀']
    negative_indicators = ['worried', 'scam', 'drop', 'sell', 'bearish']
    
    score = 0
    for doc in raw_documents:
        content_lower = doc['content'].lower()
        for indicator in positive_indicators:
            if indicator in content_lower:
                score += 1
        for indicator in negative_indicators:
            if indicator in content_lower:
                score -= 1
    
    if score > 2:
        price_change = random.uniform(3, 7)
        return f"Positive price movement (+{price_change:.2f}%)"
    elif score < -2:
        price_change = random.uniform(-7, -3)
        return f"Negative price movement ({price_change:.2f}%)"
    else:
        price_change = random.uniform(-2, 2)
        return f"Stable/Mixed price movement ({price_change:.2f}%)"