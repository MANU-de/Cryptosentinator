
import datetime
import random
from langchain_core.tools import tool
from typing import List, Dict 

@tool
def search_x_mock(keyword: str, count: int = 5) -> List[Dict]:
    """
    Simulates searching X (Twitter) for a keyword.
    Returns a list of mock tweets.
    """
    print(f"--- TOOL: Mock X Search for '{keyword}' ---")
    tweets = []
    for i in range(count):
        sentiment_type = random.choice(["positive", "negative", "neutral"])
        if sentiment_type == "positive":
            text = f"Great news for #{keyword}! To the moon! 🚀 #{keyword}IsTheFuture"
        elif sentiment_type == "negative":
            text = f"Worried about #{keyword} price drop. Is it a scam? #Sell{keyword}"
        else:
            text = f"Just observing #{keyword} market movements. #Crypto"
        tweets.append({
            "source": "X",
            "content": text,
            "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=i)).isoformat(),
            "keyword": keyword
        })
    return tweets

@tool
def search_reddit_mock(keyword: str, subreddit: str = "cryptocurrency", count: int = 3) -> List[Dict]:
    """
    Simulates searching Reddit for a keyword in a specific subreddit.
    Returns a list of mock Reddit posts.
    """
    print(f"--- TOOL: Mock Reddit Search for '{keyword}' in r/{subreddit} ---")
    posts = []
    for i in range(count):
        posts.append({
            "source": "Reddit",
            "content": f"Discussion about {keyword} on r/{subreddit}. Some say it's bullish, others bearish. What are your thoughts on {keyword}?",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(days=i)).isoformat(),
            "keyword": keyword
        })
    return posts

@tool
def search_news_mock(keyword: str, count: int = 2) -> List[Dict]:
    """
    Simulates searching news articles for a keyword.
    Returns a list of mock news articles.
    """
    print(f"--- TOOL: Mock News Search for '{keyword}' ---")
    articles = []
    for i in range(count):
        articles.append({
            "source": "NewsOutlet",
            "content": f"Major financial news outlet reports on {keyword}. Experts predict potential volatility for {keyword} in the coming weeks.",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(days=i*2)).isoformat(),
            "keyword": keyword
        })
    return articles