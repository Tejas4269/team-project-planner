import json
from .models import User
from user_base import UserBase


class UserService(UserBase):
    """Concrete implementation of UserBase using Django ORM + SQLite."""

    def create_user(self, request: str) -> str:
        data = json.loads(request)
        name = data.get("name", "")
        display_name = data.get("display_name", "")

        if not name:
            raise ValueError("name is required")
        if len(name) > 64:
            raise ValueError("name can be max 64 characters")
        if len(display_name) > 64:
            raise ValueError("display_name can be max 64 characters")
        if User.objects.filter(name=name).exists():
            raise ValueError(f"User with name '{name}' already exists")

        user = User.objects.create(name=name, display_name=display_name)
        return json.dumps({"id": str(user.id)})

    def list_users(self) -> str:
        users = User.objects.all().order_by("creation_time")
        result = [
            {
                "name": u.name,
                "display_name": u.display_name,
                "creation_time": u.creation_time.isoformat(),
            }
            for u in users
        ]
        return json.dumps(result)

    def describe_user(self, request: str) -> str:
        data = json.loads(request)
        user_id = data.get("id")
        try:
            u = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError(f"User '{user_id}' not found")
        return json.dumps(
            {
                "name": u.name,
                "display_name": u.display_name,
                "creation_time": u.creation_time.isoformat(),
            }
        )

    def update_user(self, request: str) -> str:
        data = json.loads(request)
        user_id = data.get("id")
        updates = data.get("user", {})
        try:
            u = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError(f"User '{user_id}' not found")

        if "name" in updates:
            raise ValueError("user name cannot be updated")

        display_name = updates.get("display_name", u.display_name)
        if len(display_name) > 128:
            raise ValueError("display_name can be max 128 characters")

        u.display_name = display_name
        u.save()
        return json.dumps({"id": str(u.id)})

    def get_user_teams(self, request: str) -> str:
        data = json.loads(request)
        user_id = data.get("id")
        try:
            u = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError(f"User '{user_id}' not found")

        teams = u.teams.all()
        result = [
            {
                "name": t.name,
                "description": t.description,
                "creation_time": t.creation_time.isoformat(),
            }
            for t in teams
        ]
        return json.dumps(result)
