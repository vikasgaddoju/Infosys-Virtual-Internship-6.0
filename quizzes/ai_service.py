# quizzes/ai_service.py
import json
import re
import requests
from django.conf import settings


OPENAI_API_KEY = settings.OPENAI_API_KEY
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"



def clean_json(text: str) -> str:
    """
    Removes markdown code fences and extracts JSON array from text.
    """
    text = text.strip()

    # Remove ```json or ``` fences
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
    if text.endswith("```"):
        text = text[:-3].strip()

    # Extract JSON array using regex
    match = re.search(r"(\[\s*\{.*\}\s*\])", text, flags=re.DOTALL)
    if match:
        return match.group(1)

    return text


def validate_questions(questions, count):
    """
    Ensures JSON array is valid.
    """
    if not isinstance(questions, list):
        raise ValueError("AI did not return a JSON array.")

    if len(questions) != count:
        raise ValueError(f"Expected {count} questions, got {len(questions)}.")

    required = ["question", "option_a", "option_b", "option_c", "option_d", "correct_answer"]

    for q in questions:
        for f in required:
            if f not in q:
                raise ValueError(f"Missing field: {f}")

        if q["correct_answer"] not in ["A", "B", "C", "D"]:
            raise ValueError("correct_answer must be A/B/C/D")

    return questions


def generate_quiz_questions(topic, category, difficulty, count=10):
    """
    Generate MCQs using Groq (LLaMA-3.3 70B versatile)
    """

    if not OPENAI_API_KEY:
        raise Exception("OPENAI_API_KEY not found in settings.")


    prompt = f"""
Generate {count} multiple choice questions in STRICT JSON format.

Topic: {topic}
Category: {category}
Difficulty: {difficulty}

Each item must follow EXACTLY this structure:

[
  {{
    "question": "text",
    "option_a": "A option",
    "option_b": "B option",
    "option_c": "C option",
    "option_d": "D option",
    "correct_answer": "A",
    "explanation": "why the answer is correct"
  }}
]

Return ONLY the JSON array. No text outside JSON.
"""

    try:
        response = requests.post(
            OPENAI_URL,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
            },
            timeout=45
        )

        response.raise_for_status()
        data = response.json()

        # Extract text from Groq response
        message = data["choices"][0]["message"]["content"]

        # Clean and extract JSON
        cleaned = clean_json(message)

        # Parse JSON array
        questions = json.loads(cleaned)

        # Validate structure
        return validate_questions(questions, count)

    except Exception as e:
        raise Exception(f"Failed to generate quiz questions: {e}")
