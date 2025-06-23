# tools/market_data_tools.py
import random
from langchain_core.tools import tool
from typing import Dict

@tool
def get_mock_crypto_price_data(cryptocurrency_symbol: str) -> Dict:
    """
    Simulates fetching cryptocurrency price data.
    Returns a dictionary with 'price' and '24h_change_percent'.
    """
    print(f"--- TOOL: Mock Crypto Price for '{cryptocurrency_symbol}' ---")
    # Simulate some price action
    price = random.uniform(1000, 60000)
    change = random.uniform(-5, 5)
    if "BTC" in cryptocurrency_symbol.upper():
        price = random.uniform(30000, 70000)
    elif "ETH" in cryptocurrency_symbol.upper():
        price = random.uniform(1500, 4000)
    
    return {
        "symbol": cryptocurrency_symbol,
        "price": round(price, 2),
        "24h_change_percent": round(change, 2)
    }