from django.db import models
from django.utils import timezone
from datetime import timedelta


class OTP(models.Model):
    phone = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"{self.phone} - {self.otp}"


class Lesson(models.Model):
    day = models.IntegerField()
    step = models.IntegerField()

    message = models.TextField()  # AI बोलणार
    expected_input = models.TextField(null=True, blank=True)  # optional

    next_step = models.IntegerField()

    def __str__(self):
        return f"Day {self.day} - Step {self.step}"
