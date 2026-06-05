import uuid
from django.db import models
from users.models import User


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=128, blank=True)
    admin = models.ForeignKey(User, on_delete=models.PROTECT, related_name='administered_teams')
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    creation_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
