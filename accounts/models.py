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

    # Bot message
    message = models.TextField()

    # Expected user response hint
    expected_input = models.TextField(
        null=True,
        blank=True
    )

    validation_type = models.CharField(
        max_length=50,
        default="contains"
    )


    min_words = models.IntegerField(
        default=0
    )

    # Next step number
    next_step = models.IntegerField()

    # Detect last lesson step
    is_last_step = models.BooleanField(default=False)

    def __str__(self):
        return f"Day {self.day} - Step {self.step}"


class UserProgress(models.Model):

    phone = models.CharField(max_length=15)

    completed_day = models.IntegerField(default=0)

    unlocked_day = models.IntegerField(default=1)

    current_step = models.IntegerField(default=1)

    updated_at = models.DateTimeField(auto_now=True)
    is_premium = models.BooleanField(
        default=False
    )

    def __str__(self):

        return self.phone