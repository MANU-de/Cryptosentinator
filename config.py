import os

def get_gemini_api_key():
    return os.environ.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

