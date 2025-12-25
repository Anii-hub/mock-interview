
from django.urls import path
from .views import interview_setup,resume_upload,start_interview,submit_answer,analytics
urlpatterns=[
 path('setup/',interview_setup,name='interview_setup'),
 path('resume/',resume_upload,name='resume_upload'),
 path('start/',start_interview,name='start_interview'),
 path('submit/',submit_answer,name='submit_answer'),
 path('analytics/',analytics,name='analytics'),
]
