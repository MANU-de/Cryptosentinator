import logging
from typing import List
from pydantic import BaseModel, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential


from langchain_core.tools import tool
from config import get_gemini_api_key
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import google.generativeai as genai
import json
import re


# Setup logger for this module
logger = logging.getLogger(__name__)

# --- NEW: Pydantic model for LLM output integrity check ---
class DeepAnalysisResult(BaseModel):
    sentiment_score: float
    sentiment_label: str
    entities: List[str]
    topic: str
    
    
genai.configure(api_key=get_gemini_api_key())
model = genai.GenerativeModel('gemini-2.0-flash')


# --- NEW: retry_error_callback function for logging ---
def log_after_retry_failure(retry_state):
    """Logs a detailed error message after the final retry attempt fails."""
    logger.error(
        f"LLM call failed after {retry_state.attempt_number} attempts. Last exception: {retry_state.outcome.exception()}"
    )



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
@retry(
    wait=wait_exponential(multiplier=1, min=2, max=60), # Exponential backoff: 2s, 4s, 8s...
    stop=stop_after_attempt(3), # Retry up to 3 times
    retry_error_callback=log_after_retry_failure # Log on final failure
)
def analyze_text_deeply(text_content: str) -> dict:
    """
    Analyzes text for sentiment, key entities, and topic using Gemini.
    Responds with a JSON object containing 'sentiment_score', 'sentiment_label', 
    'entities', and 'topic'.
    """
    #print(f"--- TOOL: Deep NLP Analysis for text: '{text_content[:50]}...' ---")
    logger.info(f"Analyzing text: '{text_content[:70]}...'")
    
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
    parser = JsonOutputParser(pydantic_object=DeepAnalysisResult) # Bind parser to the model
    chain = prompt | llm | parser


    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        response_json = extract_json_from_response(response_text)
        
            # Validate and parse the response using Pydantic
        response = chain.invoke({"text": text_content})
        # --- NEW: Integrity Check using Pydantic ---
        # The parser now automatically validates against DeepAnalysisResult.
        # If the LLM output doesn't match the schema, it will raise a ValidationError.
        logger.info(f"Successfully analyzed text. Topic: {response['topic']}")
        return response
    except ValidationError as e:
        logger.warning(f"LLM output validation failed for text: '{text_content[:50]}...'. Error: {e}. Falling back.")
        return {"sentiment_score": 0.0, "sentiment_label": "Neutral", "entities": [], "topic": "Unclassified"}
    except Exception as e:
        logger.error(f"An unexpected error occurred during deep analysis: {e}")
        # Re-raise the exception to allow the @retry decorator to catch it
        raise e
        
        
       # Basic validation
       # required_keys = ['sentiment_score', 'sentiment_label', 'entities', 'topic']
       # if not all(k in response_json for k in required_keys):
       #     raise ValueError("Gemini response missing required keys.")
       # if not isinstance(response_json['sentiment_score'], (float, int)):
      #      response_json['sentiment_score'] = float(response_json['sentiment_score'])
      #  if not isinstance(response_json['entities'], list):
     #       response_json['entities'] = [str(response_json['entities'])]
    #    return response_json
   # except Exception as e:
    #    print(f"Error in deep NLP tool: {e}. Falling back to neutral.")
    #    return {
     #       "sentiment_score": 0.0,
     #       "sentiment_label": "Neutral",
      #      "entities": [],
      #      "topic": "Unclassified"
      #  }

