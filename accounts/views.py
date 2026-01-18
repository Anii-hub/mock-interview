
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from interviews.models import InterviewResult

def login_view(request):
 if request.method=='POST':
  u=authenticate(username=request.POST['username'],password=request.POST['password'])
  if u: login(request,u); return redirect('dashboard')
 return render(request,'login.html')

def register_view(request):
 if request.method=='POST':
  User.objects.create_user(username=request.POST['username'],password=request.POST['password'])
  return redirect('login')
 return render(request,'register.html')

@login_required
def dashboard(request):
    results = InterviewResult.objects.filter(user=request.user)

    total_interviews = results.count()
    avg_score = round(results.aggregate(Avg("score"))["score__avg"] or 0, 1)
    last_score = results.order_by("-created_at").first()

    return render(request, "dashboard.html", {
        "total_interviews": total_interviews,
        "avg_score": avg_score,
        "last_score": last_score.score if last_score else 0
    })

def logout_view(request):
 logout(request)
 return redirect('login')
