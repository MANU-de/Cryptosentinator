
from ..graph_state import GraphState, RawDocument
from ..tools.web_search_tools import search_x_mock, search_reddit_mock, search_news_mock

class ScoutAgent:
    """The Scout Agent is responsible for gathering raw intelligence from various sources."""
    def run(self, state: GraphState) -> dict:
        print("--- AGENT: Scout ---")
        keywords = state["keywords"]
        all_raw_docs = []
        for keyword in keywords:
            print(f"Scouting for keyword: {keyword}")
            # This agent could have more complex logic to choose sources, but for now, it hits all.
            all_raw_docs.extend(search_x_mock.invoke({"keyword": keyword, "count": 2}))
            all_raw_docs.extend(search_reddit_mock.invoke({"keyword": keyword, "count": 1}))
            all_raw_docs.extend(search_news_mock.invoke({"keyword": keyword, "count": 1}))
        
        return {"raw_documents": [RawDocument(**doc) for doc in all_raw_docs]}

scout_agent = ScoutAgent()