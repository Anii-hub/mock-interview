
from django.db import models
from django.contrib.auth.models import User

class InterviewSession(models.Model):
 user=models.ForeignKey(User,on_delete=models.CASCADE)
 topic=models.CharField(max_length=50)
 difficulty=models.CharField(max_length=20)
 mode=models.CharField(max_length=20)
 score=models.FloatField()
 created_at=models.DateTimeField(auto_now_add=True)
class InterviewResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.score}"
