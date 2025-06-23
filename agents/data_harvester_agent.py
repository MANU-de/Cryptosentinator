# agents/data_harvester_agent.py
from typing import List
from ..graph_state import GraphState, RawDocument # Relative import
from ..tools.web_search_tools import search_x_mock, search_reddit_mock, search_news_mock # Relative import

class DataHarvesterAgent:
    def __init__(self):
        self.x_tool = search_x_mock
        self.reddit_tool = search_reddit_mock
        self.news_tool = search_news_mock

    def run(self, state: GraphState) -> dict:
        print("--- AGENT: Data Harvester Running ---")
        keywords = state.get("keywords", [])
        if not keywords:
            return {"error_message": "No keywords provided to Data Harvester."}

        all_raw_docs: List[RawDocument] = []
        for keyword in keywords:
            print(f"Harvesting data for keyword: {keyword}")
            try:
                # For simplicity, we'll call each tool. In a real system, you might have logic
                # to choose tools or use an LLM to decide.
                x_results = self.x_tool.invoke({"keyword": keyword, "count": 2})
                all_raw_docs.extend(x_results)

                reddit_results = self.reddit_tool.invoke({"keyword": keyword, "count": 1})
                all_raw_docs.extend(reddit_results)
                
                news_results = self.news_tool.invoke({"keyword": keyword, "count": 1})
                all_raw_docs.extend(news_results)

            except Exception as e:
                print(f"Error during harvesting for {keyword}: {e}")
                # Continue with other keywords or data
        
        # Ensure raw_documents are properly typed
        typed_raw_docs: List[RawDocument] = [
            RawDocument(source=doc['source'], content=doc['content'], timestamp=doc['timestamp'], keyword=doc['keyword'])
            for doc in all_raw_docs
        ]

        print(f"Harvested {len(typed_raw_docs)} documents.")
        return {"raw_documents": typed_raw_docs}

data_harvester_agent = DataHarvesterAgent()