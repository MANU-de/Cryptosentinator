# agents/scout_agent.py
from datetime import datetime, timezone
from graph_state import GraphState, RawDocument
from tools.web_search_tools import search_x_mock, search_reddit_mock, search_news_mock
from tools.market_tools import fetch_binance_derivatives_data, fetch_defillama_tvl

class ScoutAgent:
    """
    The Scout Agent is responsible for gathering raw multi-modal intelligence:
    - Social sentiment (X, Reddit)
    - News narratives
    - Real-time Derivatives & Funding metrics (Binance)
    - On-Chain / TVL trends (DefiLlama)
    """

    def _normalize_symbol(self, keyword: str) -> str:
        mapping = {
            "bitcoin": "BTC",
            "btc": "BTC",
            "ethereum": "ETH",
            "eth": "ETH",
            "solana": "SOL",
            "sol": "SOL"
        }
        return mapping.get(keyword.lower().strip(), keyword.upper())

    def run(self, state: GraphState) -> dict:
        print("--- AGENT: Scout (Multi-Source & On-Chain) ---")
        keywords = state["keywords"]
        all_raw_docs = []
        current_time = datetime.now(timezone.utc).isoformat()

        for keyword in keywords:
            print(f"Scouting intelligence for: {keyword}")
            symbol = self._normalize_symbol(keyword)

            # ---------------------------------------------------------
            # 1. On-Chain & Derivatives Intelligence (Live API)
            # ---------------------------------------------------------
            deriv_data = fetch_binance_derivatives_data(symbol)
            if deriv_data and "last_price" in deriv_data:
                content = (
                    f"Market Microstructure & Derivatives for {symbol}:\n"
                    f"- Current Price: ${deriv_data.get('last_price', 'N/A')}\n"
                    f"- 24h Change: {deriv_data.get('price_change_pct_24h', 0.0)}%\n"
                    f"- 8h Funding Rate: {deriv_data.get('funding_rate_pct', 'N/A')}%\n"
                    f"- Leverage Positioning Bias: {deriv_data.get('funding_sentiment', 'Neutral')}"
                )
                all_raw_docs.append({
                    "content": content,
                    "source": "binance_derivatives",
                    "keyword": keyword,                   # <-- Added required field
                    "timestamp": current_time              # <-- Added required field
                })

            # Check chain TVL if relevant
            if symbol in ["ETH", "SOL", "BTC"]:
                chain_name = "Ethereum" if symbol == "ETH" else ("Solana" if symbol == "SOL" else "Bitcoin")
                tvl_data = fetch_defillama_tvl(chain_name.lower())
                if tvl_data:
                    content = (
                        f"On-Chain DeFi TVL for {chain_name}:\n"
                        f"- Total TVL: ${tvl_data.get('tvl_usd', 0):,}\n"
                        f"- 24h TVL Change: {tvl_data.get('tvl_24h_change_pct', 0.0)}%"
                    )
                    all_raw_docs.append({
                        "content": content,
                        "source": "defillama_onchain",
                        "keyword": keyword,               # <-- Added required field
                        "timestamp": current_time          # <-- Added required field
                    })

            # ---------------------------------------------------------
            # 2. Social Media & News Gathering
            # ---------------------------------------------------------
            # Social: X / Twitter
            try:
                x_docs = search_x_mock.run({"keyword": keyword, "count": 2})
                all_raw_docs.extend(x_docs)
            except Exception as e:
                print(f"Error gathering X docs: {e}")

            # Social: Reddit
            try:
                reddit_docs = search_reddit_mock.run({"keyword": keyword, "count": 1})
                all_raw_docs.extend(reddit_docs)
            except Exception as e:
                print(f"Error gathering Reddit docs: {e}")

            # Curated News
            try:
                news_docs = search_news_mock.run({"keyword": keyword, "count": 2})
                all_raw_docs.extend(news_docs)
            except Exception as e:
                print(f"Error gathering News docs: {e}")

        # Construct RawDocument objects
        normalized_documents = []
        for doc in all_raw_docs:
            if isinstance(doc, dict):
                normalized_documents.append(RawDocument(**doc))
            elif isinstance(doc, RawDocument):
                normalized_documents.append(doc)

        print(f"Scout completed: collected {len(normalized_documents)} multi-source documents.")
        return {"raw_documents": normalized_documents}

scout_agent = ScoutAgent()