
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .ai_engine import generate_question, generate_resume_based_question,evaluate_full_interview
import PyPDF2, re
from .models import InterviewResult

@login_required
def interview_setup(request):
 return render(request,'interview_setup.html')

@login_required
def resume_upload(request):
    if request.method == "POST":
        resume_file = request.FILES.get("resume")

        if not resume_file or not resume_file.name.endswith(".pdf"):
            return render(request, "resume_upload.html", {
                "error": "Please upload a valid PDF file."
            })

        reader = PyPDF2.PdfReader(resume_file)
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        if len(text.strip()) < 200:
            return render(request, "resume_upload.html", {
                "error": "Unable to read resume content."
            })

        request.session["resume_text"] = text
        request.session["resume_uploaded"] = True

        return redirect("interview_setup")

    return render(request, "resume_upload.html")


@login_required
def start_interview(request):
    if request.method != "POST":
        return redirect("interview_setup")

    difficulty = request.POST["difficulty"]
    mode = request.POST["mode"]
    total_questions = int(request.POST["num_questions"])

    #  Clear previous interview data
    request.session["questions"] = []
    request.session["answers"] = []
    request.session["current_index"] = 0
    request.session["total_questions"] = total_questions
    request.session["difficulty"] = difficulty
    request.session["mode"] = mode

    resume_text = request.session.get("resume_text")

    #  GENERATE FIRST QUESTION HERE
    if mode == "resume" and resume_text:
        first_question = generate_resume_based_question(
            resume_text=resume_text,
            difficulty=difficulty
        )
        request.session["topic"] = "Resume-Based"
    else:
        topic = request.POST["topic"]
        first_question = generate_question(topic, difficulty)
        request.session["topic"] = topic

    #  STORE FIRST QUESTION
    request.session["questions"].append(first_question)

    return render(request, "interview.html", {
        "question": first_question,
        "current": 1,
        "total": total_questions
    })
    

@login_required
def submit_answer(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    answer = request.POST.get("answer", "").strip()
    if not answer:
        return JsonResponse({"error": "Please provide an answer."}, status=400)

    #  Voice confidence inputs
    voice_words = int(request.POST.get("voice_words", 0))
    voice_duration = float(request.POST.get("voice_duration", 0))

    if voice_duration > 0:
        speech_rate = voice_words / voice_duration
        voice_confidence = min(10, max(1, int(speech_rate * 2)))
    else:
        voice_confidence = 1

    questions = request.session.get("questions", [])
    answers = request.session.get("answers", [])
    current_index = request.session.get("current_index", 0)
    total_questions = request.session.get("total_questions", 1)
    difficulty = request.session.get("difficulty")
    mode = request.session.get("mode")
    resume_text = request.session.get("resume_text")
    topic = request.session.get("topic")

    answers.append(answer)
    request.session["answers"] = answers

    current_index += 1
    request.session["current_index"] = current_index

    #  NEXT QUESTION
    if current_index < total_questions:
        if mode == "resume" and resume_text:
            next_question = generate_resume_based_question(resume_text, difficulty)
        else:
            next_question = generate_question(topic, difficulty)

        questions.append(next_question)
        request.session["questions"] = questions

        return JsonResponse({
            "next_question": next_question,
            "current": current_index + 1,
            "total": total_questions
        })

    #  FINAL FEEDBACK
    final_feedback = evaluate_full_interview(questions, answers)

    match = re.search(r'OVERALL SCORE:\s*(\d+)', final_feedback)
    score = int(match.group(1)) if match else 0

    InterviewResult.objects.create(
        user=request.user,
        score=score,
        difficulty=difficulty,
        mode="Resume-Based" if mode == "resume" else "General",
        voice_confidence=voice_confidence
    )

    return JsonResponse({
        "final_feedback": final_feedback
    })






@login_required
def analytics(request):
    results = InterviewResult.objects.filter(user=request.user).order_by("created_at")

    scores = [r.score for r in results]
    dates = [r.created_at.strftime("%d %b") for r in results]

    total_interviews = results.count()
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    best_score = max(scores) if scores else 0
    last_score = scores[-1] if scores else 0

    return render(request, "analytics.html", {
        "scores": scores,
        "dates": dates,
        "total_interviews": total_interviews,
        "avg_score": avg_score,
        "best_score": best_score,
        "last_score": last_score,
        "results": results
    })
