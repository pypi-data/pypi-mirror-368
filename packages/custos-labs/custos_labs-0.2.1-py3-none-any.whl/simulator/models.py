# simulator/models.py

from django.db import models
from django.contrib.auth.models import User
from api.models import APIKey

class SimulationRun(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    api_key = models.ForeignKey(APIKey, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(
        max_length=32,
        choices=[
            ("active", "Active"),
            ("misaligned", "Misaligned"),
            ("completed", "Completed"),
            ("warning", "Warning"),
        ],
        default="active"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    alignment_score = models.FloatField(default=100.0)

    def __str__(self):
        return f"Run #{self.id} - {self.user.username}"

class SimulatorLog(models.Model):
    run = models.ForeignKey(SimulationRun, on_delete=models.CASCADE, related_name="logs")
    timestamp = models.DateTimeField(auto_now_add=True)
    response = models.TextField()
    alignment_score = models.FloatField()
    color = models.CharField(max_length=8) 
    flatline = models.BooleanField(default=False)
    violations = models.JSONField(default=list)
    confidence = models.FloatField(default=1.0)
    prompt = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Log {self.id} [{self.color}] for Run {self.run.id}"
