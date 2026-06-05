import uuid
from django.db import models
from teams.models import Team
from users.models import User


class Board(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN'
        CLOSED = 'CLOSED'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='boards')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    creation_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('name', 'team')

    def __str__(self):
        return f"{self.name} ({self.team.name})"


class Task(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN'
        IN_PROGRESS = 'IN_PROGRESS'
        COMPLETE = 'COMPLETE'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=128, blank=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    assigned_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='tasks')
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN)
    creation_time = models.DateTimeField()

    class Meta:
        unique_together = ('title', 'board')

    def __str__(self):
        return f"{self.title} [{self.status}]"
