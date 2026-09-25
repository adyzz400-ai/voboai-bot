"""
VoboAi — Gemini AI solver.

Sends each Sparx question to Gemini and returns the answer.
Uses the gemini-2.0-flash model via the google-genai SDK.
"""
import google.generativeai as genai

from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
_model = genai.GenerativeModel("gemini-2.0-flash")


def solve_question(question_text: str, image_bytes: bytes = None) -> str:
    """
    Solve a single Sparx question.

    question_text: the text of the question.
    image_bytes:   optional screenshot/PNG of the question (for image solving).
    """
    parts = [question_text]
    if image_bytes:
        parts.append({"mime_type": "image/png", "data": image_bytes})

    prompt = (
        "You are solving a Sparx Maths question. Answer concisely and exactly "
        "what the answer box expects (a number, expression, or short text). "
        "Do not explain. Just give the answer.\n\n"
        f"Question: {question_text}"
    )

    response = _model.generate_content(prompt)
    return response.text.strip()
