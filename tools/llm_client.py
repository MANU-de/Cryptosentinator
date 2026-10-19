# tools/llm_client.py
import os
import re
import json

# Check for Gemini availability
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
gemini_model = None
if GEMINI_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        gemini_model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
    except Exception as e:
        print(f"Gemini init error: {e}")

# Hugging Face Serverless Client
hf_client = None
try:
    from huggingface_hub import InferenceClient
    # Inside Hugging Face Spaces, HF_TOKEN is injected automatically
    hf_token = os.getenv("HF_TOKEN")
    hf_client = InferenceClient(model="Qwen/Qwen2.5-72B-Instruct", token=hf_token)
except Exception as e:
    print(f"HF Client init error: {e}")


def generate_strategic_json(prompt: str) -> dict:
    """
    Model-agnostic LLM caller:
    1. Attempts Google Gemini first if configured.
    2. Gracefully falls back to Hugging Face Inference (Qwen 2.5 72B) if Gemini fails or is omitted.
    """
    response_text = ""

    # Strategy 1: Google Gemini
    if gemini_model:
        try:
            res = gemini_model.generate_content(prompt)
            if res and res.text:
                response_text = res.text.strip()
        except Exception as e:
            print(f"[LLM Router] Gemini failed ({e}). Falling back to Hugging Face Inference...")

    # Strategy 2: Hugging Face Serverless (Qwen 2.5 72B)
    if not response_text and hf_client:
        try:
            print("[LLM Router] Using Hugging Face Serverless Inference (Qwen/Qwen2.5-72B-Instruct)...")
            messages = [
                {"role": "system", "content": "You are a professional quantitative crypto market strategist. Output ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ]
            res = hf_client.chat_completion(messages=messages, max_tokens=1000, temperature=0.2)
            response_text = res.choices[0].message.content.strip()
        except Exception as e:
            print(f"[LLM Router] HF Inference error: {e}")

    # Parse JSON from output
    try:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        print(f"Error parsing JSON from LLM: {e}")

    return {}