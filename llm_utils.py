"""Interface to Gemini API for health recommendations and medical Q&A."""
import os
import json
from typing import Dict, List, Any
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)


def get_recommendations(user_json: Dict[str, Any], cluster: str, risks: List[str], pdf_text: str) -> str:
    if not API_KEY:
        return "[Error: Missing Gemini API key]"

    prompt = f"""
You are a compassionate AI healthcare assistant. Analyze the user's health profile and return 3 structured sections:

1. **Health Overview** - Explain the user's health status and risk level.
2. **Personalized Action Plan** - Give 5-8 steps sorted from easiest to most critical (e.g. hydration, diet, doctor visit).
3. **Medical Record Analysis** - If lab or clinical data is found, explain it. If not, return: (no lab records uploaded)

USER DATA:
{json.dumps(user_json, indent=2)}

RISK CLUSTER: {cluster.upper()}
IDENTIFIED RISK FACTORS: {', '.join(risks)}

MEDICAL RECORD TEXT:
{pdf_text if pdf_text else '(no medical records uploaded)'}
"""

    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[Gemini Error] {str(e)}"


def chat_with_gemini_with_context(user_input: str, medical_records: str) -> str:
    if not API_KEY:
        return "[Error: Missing Gemini API key]"

    system_prompt = (
        "You are a medical expert assistant. Answer only medical-related questions. "
        "Use clinical knowledge and any provided records. If no relevant info, say so."
    )

    prompt = f"""
{system_prompt}

USER QUESTION:
{user_input}

MEDICAL RECORDS:
{medical_records if medical_records else '(no records provided)'}
"""

    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[Gemini Error] {str(e)}"
