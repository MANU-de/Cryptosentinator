# agents/intelligence_analyst_agent.py
import re
from graph_state import GraphState, ProcessedDocument

# Curated Crypto Narrative Taxonomy
NARRATIVE_TAXONOMY = {
    "Derivatives & Leverage Dynamics": [
        "funding rate", "leverage", "liquidation", "perpetual", "futures", "open interest", "short squeeze"
    ],
    "DeFi & On-Chain Health": [
        "tvl", "on-chain", "defi", "staking", "yield", "protocol", "ethereum tvl", "solana tvl"
    ],
    "Institutional & Macro Flows": [
        "etf", "blackrock", "institutional", "fed", "inflation", "interest rate", "sec", "treasury"
    ],
    "Retail Momentum & Social Buzz": [
        "moon", "fomo", "fud", "hodl", "community", "retail", "viral", "sentiment", "pump"
    ],
    "Price Action & Market Momentum": [
        "breakout", "resistance", "support", "ath", "consolidation", "rally", "volume", "24h"
    ]
}

class IntelligenceAnalystAgent:
    """
    Refined Analyst Agent:
    - Identifies dominant crypto narratives per document.
    - Evaluates nuanced sentiment for on-chain, derivatives, and social data.
    - Returns ProcessedDocument objects matching GraphState.
    """

    def detect_narrative(self, content: str, source: str) -> str:
        """Classifies content into a specific crypto narrative."""
        content_lower = content.lower()

        # Priority routing for structured feeds
        if "derivatives" in source or "funding" in content_lower:
            return "Derivatives & Leverage Dynamics"
        if "onchain" in source or "tvl" in content_lower:
            return "DeFi & On-Chain Health"

        # Keyword frequency matching across taxonomy
        best_narrative = "General Market Trend"
        max_matches = 0

        for narrative, keywords in NARRATIVE_TAXONOMY.items():
            matches = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', content_lower))
            if matches > max_matches:
                max_matches = matches
                best_narrative = narrative

        return best_narrative

    def calculate_sentiment(self, doc: dict) -> tuple[float, str]:
        """
        Calculates source-aware sentiment score and label:
        - Derivatives: Evaluates funding rates and price changes.
        - On-Chain: Evaluates TVL trajectory.
        - Social/News: Scored for emotional retail conviction.
        """
        source = doc.get("source", "")
        content = doc.get("content", "")
        score = 0.0

        # 1. Derivatives Sentiment logic
        if "derivatives" in source:
            if "Heavy Bullish" in content or "Long Leverage" in content:
                score += 0.4
            elif "Bearish" in content or "Short Leverage" in content:
                score -= 0.4
            
            match = re.search(r'24h Change:\s*([+-]?\d+(?:\.\d+)?)%', content)
            if match:
                change = float(match.group(1))
                score += min(max(change / 20.0, -0.5), 0.5)

        # 2. On-Chain TVL logic
        elif "onchain" in source:
            match = re.search(r'24h TVL Change:\s*([+-]?\d+(?:\.\d+)?)%', content)
            if match:
                tvl_change = float(match.group(1))
                score = min(max(tvl_change / 10.0, -1.0), 1.0)
            else:
                score = 0.1

        # 3. Social / News NLP logic
        else:
            content_lower = content.lower()
            bull_words = ["bull", "surge", "buying", "accumulate", "optimistic", "growth", "high", "rally"]
            bear_words = ["bear", "drop", "dump", "cautious", "fear", "regulatory", "fud", "fall"]

            bull_count = sum(1 for w in bull_words if w in content_lower)
            bear_count = sum(1 for w in bear_words if w in content_lower)

            if bull_count + bear_count > 0:
                score = (bull_count - bear_count) / (bull_count + bear_count)

        score = round(min(max(score, -1.0), 1.0), 2)
        
        # Determine label
        if score > 0.15:
            label = "Bullish"
        elif score < -0.15:
            label = "Bearish"
        else:
            label = "Neutral"

        return score, label

    def run(self, state: GraphState) -> dict:
        print("--- AGENT: Intelligence Analyst (Narrative Detection) ---")
        raw_docs = state["raw_documents"]
        processed_docs: list[ProcessedDocument] = []
        narrative_counts: dict[str, int] = {}

        for doc in raw_docs:
            doc_dict = dict(doc)

            # 1. Detect dynamic narrative
            narrative = self.detect_narrative(doc_dict.get("content", ""), doc_dict.get("source", ""))
            narrative_counts[narrative] = narrative_counts.get(narrative, 0) + 1

            # 2. Compute sentiment score and label
            score, label = self.calculate_sentiment(doc_dict)

            # 3. Build ProcessedDocument matching your TypedDict
            processed_doc = ProcessedDocument(
                source=doc_dict.get("source", ""),
                content=doc_dict.get("content", ""),
                timestamp=doc_dict.get("timestamp", ""),
                keyword=doc_dict.get("keyword", ""),
                sentiment_score=score,
                sentiment_label=label,
                topic=narrative,
                entities=[doc_dict.get("keyword", "")]
            )
            processed_docs.append(processed_doc)

        print(f"Analyst completed: Processed {len(processed_docs)} documents.")
        print(f"Identified Narratives: {narrative_counts}")

        return {"processed_documents": processed_docs}

intelligence_analyst_agent = IntelligenceAnalystAgent()