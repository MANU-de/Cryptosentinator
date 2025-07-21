
from langchain_core.tools import tool
from ..config import get_gemini_api_key
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import google.generativeai as genai
import json
import re


genai.configure(api_key=get_gemini_api_key())
model = genai.GenerativeModel('gemini-2.0-flash')

def extract_json_from_response(response_text: str) -> dict:
    """
    Extracts JSON from Gemini's response, even if wrapped in markdown code blocks.
    """
    # Remove markdown code block if present
    code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    if code_block_match:
        json_str = code_block_match.group(1)
    else:
        # Fallback: try to find the first {...} block
        json_match = re.search(r"(\{.*\})", response_text, re.DOTALL)
        json_str = json_match.group(1) if json_match else response_text
    # Try to parse
    return json.loads(json_str)


@tool
def analyze_text_deeply(text_content: str) -> dict:
    """
    Analyzes text for sentiment, key entities, and topic using Gemini.
    Responds with a JSON object containing 'sentiment_score', 'sentiment_label', 
    'entities', and 'topic'.
    """
    print(f"--- TOOL: Deep NLP Analysis for text: '{text_content[:50]}...' ---")
    
    topic_categories = [
        "Technology Update", "Price Speculation", "Regulation", 
        "Community Discussion", "Partnership News", "General Market Trend"
    ]
    
    prompt = (
        "You are a precise financial NLP model. Analyze the following text and return a JSON object with four keys:\n"
        "1. 'sentiment_score': A float from -1.0 (very negative) to 1.0 (very positive).\n"
        "2. 'sentiment_label': A string ('Positive', 'Negative', 'Neutral').\n"
        "3. 'entities': A list of key strings (crypto names, projects, events).\n"
        f"4. 'topic': Classify the text into ONE of the following categories: {topic_categories}.\n\n"
        "Respond ONLY with the JSON object.\n\n"
        f"Text to analyze: {text_content}"
    )

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        response_json = extract_json_from_response(response_text)
        # Basic validation
        required_keys = ['sentiment_score', 'sentiment_label', 'entities', 'topic']
        if not all(k in response_json for k in required_keys):
            raise ValueError("Gemini response missing required keys.")
        if not isinstance(response_json['sentiment_score'], (float, int)):
            response_json['sentiment_score'] = float(response_json['sentiment_score'])
        if not isinstance(response_json['entities'], list):
            response_json['entities'] = [str(response_json['entities'])]
        return response_json
    except Exception as e:
        print(f"Error in deep NLP tool: {e}. Falling back to neutral.")
        return {
            "sentiment_score": 0.0,
            "sentiment_label": "Neutral",
            "entities": [],
            "topic": "Unclassified"
        }

