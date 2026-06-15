from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Student(AbstractUser):
    student_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.student_id})"


class Position(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Candidate(models.Model):
    name = models.CharField(max_length=100)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='candidates')
    photo = models.ImageField(upload_to='candidates/')
    manifesto = models.TextField()
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.position.name}"


class Vote(models.Model):
    voter = models.ForeignKey(Student, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'position')

    def __str__(self):
        return f"{self.voter.username} voted for {self.candidate.name}"


class ElectionStatus(models.Model):
    is_open = models.BooleanField(default=False)
    results_published = models.BooleanField(default=False)
    title = models.CharField(max_length=200, default="College Election 2026")
    start_time = models.DateTimeField(null=True, blank=True, help_text="Voting opens automatically at this time")
    end_time = models.DateTimeField(null=True, blank=True, help_text="Voting closes automatically at this time")

    class Meta:
        verbose_name_plural = "Election Status"

    def is_currently_open(self):
        """Returns True if election is open (respects start/end times if set)."""
        if not self.is_open:
            return False
        now = timezone.now()
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time:
            return False
        return True

    def __str__(self):
        return f"Election: {'Open' if self.is_open else 'Closed'}"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('vote', 'Vote Cast'),
        ('register', 'Registration'),
        ('failed_login', 'Failed Login'),
    ]

    user = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=150, blank=True)  # Store even if user deleted
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    detail = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Audit Log Entry"
        verbose_name_plural = "Audit Log"

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.username} — {self.get_action_display()}"
