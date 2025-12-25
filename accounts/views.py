
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

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
 return render(request,'dashboard.html')

def logout_view(request):
 logout(request)
 return redirect('login')
