# tools/market_tools.py
import requests
from tools.cache_utils import disk_cache

@disk_cache(ttl_seconds=300)
def fetch_binance_derivatives_data(symbol: str = "BTC") -> dict:
    """Fetches real-time funding rate and 24h ticker with 5-minute disk cache."""
    pair = f"{symbol.upper()}USDT"
    data = {}

    # 1. Fetch Funding Rate
    try:
        url_funding = f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={pair}&limit=1"
        res = requests.get(url_funding, timeout=5)
        if res.status_code == 200 and res.json():
            latest = res.json()[0]
            rate = float(latest.get("fundingRate", 0.0)) * 100
            data["funding_rate_pct"] = round(rate, 4)
            data["funding_sentiment"] = "Heavy Bullish / Long Leverage" if rate > 0.03 else ("Bearish / Short Leverage" if rate < 0 else "Neutral")
    except Exception as e:
        data["funding_rate_error"] = str(e)

    # 2. Fetch 24h Price Change & Volume
    try:
        url_ticker = f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}"
        res = requests.get(url_ticker, timeout=5)
        if res.status_code == 200:
            ticker = res.json()
            data["price_change_pct_24h"] = round(float(ticker.get("priceChangePercent", 0.0)), 2)
            data["last_price"] = float(ticker.get("lastPrice", 0.0))
            data["volume_quote"] = round(float(ticker.get("quoteVolume", 0.0)), 2)
    except Exception as e:
        data["ticker_error"] = str(e)

    return data


@disk_cache(ttl_seconds=300)
def fetch_defillama_tvl(protocol_or_chain: str = "ethereum") -> dict:
    """Fetches DeFi TVL growth with 5-minute disk cache."""
    try:
        url = f"https://api.llama.fi/v2/historicalChainTvl/{protocol_or_chain}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200 and len(res.json()) >= 2:
            data = res.json()
            latest_tvl = data[-1]["tvl"]
            prev_tvl = data[-2]["tvl"]
            tvl_change_pct = round(((latest_tvl - prev_tvl) / prev_tvl) * 100, 2)
            return {"chain": protocol_or_chain, "tvl_usd": round(latest_tvl, 2), "tvl_24h_change_pct": tvl_change_pct}
    except Exception:
        pass
    return {}