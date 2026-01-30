
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
You are a senior technical interviewer at a top tech company.

Below is a full interview transcript:
{qa_text}

Evaluate the candidate holistically.

Give:
1. Numeric scores per skill (0–10)
2. Detailed professional feedback
3. Hiring readiness

Respond in EXACTLY this format:

OVERALL SCORE: X/10

SKILL SCORES:
- Technical Knowledge: X/10
- Problem Solving: X/10
- Communication: X/10
- Confidence: X/10
- Interview Readiness: X/10

TECHNICAL ASSESSMENT:
- Depth of understanding
- Accuracy of concepts
- Practical reasoning

COMMUNICATION & CLARITY:
- Explanation quality
- Structure of answers
- Confidence while explaining

STRENGTHS:
- Specific strengths observed

WEAKNESSES:
- Specific gaps or mistakes

IMPROVEMENT SUGGESTIONS:
- Actionable next steps
- Topics to focus on

HIRING RECOMMENDATION:
- Strong Hire / Hire / Borderline / No Hire
- Suitable level (Junior / Mid / Senior)
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
