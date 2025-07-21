# tools/nlp_tools.py
from langchain_core.tools import tool
from ..config import get_gemini_api_key
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParse
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

'''@tool
def analyze_sentiment_and_extract_entities(text_content: str) -> dict:
    """
    Analyzes the sentiment of a given text and extracts key entities
    using Gemini. Returns a dictionary with 'sentiment_score' (float -1 to 1),
    'sentiment_label' (Positive, Negative, Neutral), and 'entities' (list of strings).
    """
    print(f"--- TOOL: Gemini NLP for text: '{text_content[:50]}...' ---")
    prompt = (
        "You are an expert NLP model. Analyze the following text for sentiment and key entities "
        "(especially cryptocurrency names, project names, or market-related events). "
        "Respond ONLY with a JSON object with three keys: "
        "'sentiment_score' (a float between -1.0 for very negative and 1.0 for very positive), "
        "'sentiment_label' (string: 'Positive', 'Negative', or 'Neutral'), and "
        "'entities' (a list of strings).\n\n"
        f"Text to analyze: {text_content}"
    )

    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            # Robustly extract JSON
            response_json = extract_json_from_response(response_text)
            # Basic validation
            if not all(k in response_json for k in ['sentiment_score', 'sentiment_label', 'entities']):
                raise ValueError("Gemini response missing required keys.")
            if not isinstance(response_json['sentiment_score'], (float, int)):
                response_json['sentiment_score'] = float(response_json['sentiment_score'])
            if not isinstance(response_json['entities'], list):
                response_json['entities'] = [str(response_json['entities'])]
            return response_json
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error processing Gemini response (attempt {attempt+1}/{max_retries}): {e}. Retrying if last attempt.")
            if attempt == max_retries - 1:
                print("Gemini NLP tool failed after retries. Returning neutral sentiment and no entities.")
                return {"sentiment_score": 0.0, "sentiment_label": "Neutral", "entities": []}
        except Exception as e:
            print(f"An unexpected error occurred in Gemini NLP tool (attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                print("Gemini NLP tool failed after retries. Returning neutral sentiment and no entities.")
                return {"sentiment_score": 0.0, "sentiment_label": "Neutral", "entities": []}

    return {"sentiment_score": 0.0, "sentiment_label": "Neutral", "entities": []} '''

@tool
def analyze_text_deeply(text_content: str) -> dict:
    """
    Analyzes text for sentiment, key entities, and topic.
    Responds with a JSON object containing 'sentiment_score', 'sentiment_label', 
    'entities', and 'topic'.
    """
    print(f"--- TOOL: Deep NLP Analysis for text: '{text_content[:50]}...' ---")
    
    topic_categories = ["Technology Update", "Price Speculation", "Regulation", "Community Discussion", "Partnership News", "General Market Trend"]
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", f"""You are a precise financial NLP model. Analyze the text and return a JSON object with four keys:
        1. 'sentiment_score': A float from -1.0 (very negative) to 1.0 (very positive).
        2. 'sentiment_label': A string ('Positive', 'Negative', 'Neutral').
        3. 'entities': A list of key strings (crypto names, projects, events).
        4. 'topic': Classify the text into ONE of the following categories: {topic_categories}.
        
        Respond ONLY with the JSON object."""),
        ("user", "Text to analyze: {text}")
    ])
    
    parser = JsonOutputParser()
    chain = prompt_template | llm | parser

    try:
        response = chain.invoke({"text": text_content})
        # Basic validation
        if not all(k in response for k in ['sentiment_score', 'sentiment_label', 'entities', 'topic']):
            raise ValueError("LLM response missing required keys.")
        return response
    except Exception as e:
        print(f"Error in deep NLP tool: {e}. Falling back to neutral.")
        return {
            "sentiment_score": 0.0,
            "sentiment_label": "Neutral",
            "entities": [],
            "topic": "Unclassified"
        }

# Example of a simpler, non-LLM based sentiment tool (like VADER) if you wanted an alternative
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# analyzer = SentimentIntensityAnalyzer()
# @tool
# def vader_sentiment(text_content: str) -> float:
#     """Analyzes sentiment using VADER. Returns compound score."""
#     vs = analyzer.polarity_scores(text_content)
#     return vs['compound']