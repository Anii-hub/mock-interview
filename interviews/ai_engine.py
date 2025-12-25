
import os
from google import genai

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "models/gemini-flash-latest"
import re

def clean_question(text: str) -> str:
    if not text:
        return ""

    # Remove markdown symbols
    text = re.sub(r'[*#>`_]', '', text)

    # Remove common AI prefixes
    text = re.sub(
        r'(?i)(here is|this is|below is|following is|interview question|question)\s*[:\-]?',
        '',
        text
    )

    # Remove bonus / explanation sections
    text = re.split(
        r'(?i)bonus|consideration|explanation|note',
        text
    )[0]

    # Remove numbering
    text = re.sub(r'^(Q\\.?\\d+|\\d+\\.)\\s*', '', text)

    # Remove code block markers
    text = text.replace("```python", "").replace("```", "")

    return text.strip()


def generate_question(topic, difficulty):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=f"""
        Generate ONE interview question for {difficulty} level {topic}.
        Output ONLY the question.
        """
    )

    return clean_question(response.text)

def generate_resume_based_question(resume_text, difficulty):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=f"""
        You are an interviewer.

        Below is the candidate's resume content:
        {resume_text[:1500]}

        Task:
        - Identify the candidate's primary technical domain
        - Generate ONE {difficulty}-level interview question
        - Base the question strictly on the resume
        - Output ONLY the question
        """
    )

    return clean_question(response.text)


def evaluate_full_interview(questions, answers):
    qa_text = ""
    for i, (q, a) in enumerate(zip(questions, answers), start=1):
        qa_text += f"""
Question {i}:
{q}

Answer {i}:
{a}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=f"""
        You are a professional interviewer.

        Below is a complete interview transcript:
        {qa_text}

        Task:
        - Evaluate the overall performance
        - Do NOT evaluate question by question
        - Provide a final interview-style assessment

        Respond in this EXACT format:

        OVERALL SCORE: X/10

        STRENGTHS:
        - point
        - point

        WEAKNESSES:
        - point
        - point

        IMPROVEMENT SUGGESTIONS:
        - point
        - point
        """
    )

    return response.text.strip()


import time
from google.genai.errors import ClientError

def safe_generate(call_fn):
    try:
        return call_fn()
    except ClientError as e:
        if "RESOURCE_EXHAUSTED" in str(e):
            time.sleep(3)
            return call_fn()
        raise
def generate_question(topic, difficulty):
    return safe_generate(lambda: client.models.generate_content(
        model=MODEL_NAME,
        contents=f"Ask one {difficulty} interview question on {topic}."
    )).text
