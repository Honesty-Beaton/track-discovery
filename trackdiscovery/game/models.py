from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class GameSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=10, choices=[('Easy', 'Easy'), ('Normal', 'Normal'), ('Hard', 'Hard')])
    gameMode = models.CharField(max_length=15, choices=[('Song Snippet', 'Song Snippet'), ('Album Cover', 'Album Cover')])
    score = models.IntegerField(default=0)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Question(models.Model):
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='questions')
    snippetUrl = models.URLField()
    correctAnswer = models.CharField(max_length=255)
    userAnswer = models.CharField(max_length=255, blank=True, null=True)
    isCorrect = models.BooleanField(default=False)

