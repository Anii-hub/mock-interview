# AI Mock Interview System

An AI-powered mock interview platform built using Django and Gemini AI.

## Features
- Multi-question mock interviews
- Resume-based interview questions
- Voice input & voice-based question reading
- Final consolidated interview feedback
- Performance analytics dashboard
- Secure authentication system

## Tech Stack
- Backend: Django
- Frontend: HTML, CSS, Bootstrap, JavaScript
- AI: Google Gemini API
- Database: SQLite

## Setup Instructions
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
