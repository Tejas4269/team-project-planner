import json
from team_base import TeamBase
from users.models import User
from .models import Team


class TeamService(TeamBase):
    """Concrete implementation of TeamBase using Django ORM + SQLite."""

    def create_team(self, request: str) -> str:
        data = json.loads(request)
        name = data.get("name", "")
        description = data.get("description", "")
        admin_id = data.get("admin")

        if not name:
            raise ValueError("name is required")
        if len(name) > 64:
            raise ValueError("name can be max 64 characters")
        if len(description) > 128:
            raise ValueError("description can be max 128 characters")
        if Team.objects.filter(name=name).exists():
            raise ValueError(f"Team '{name}' already exists")

        try:
            admin = User.objects.get(id=admin_id)
        except User.DoesNotExist:
            raise ValueError(f"Admin user '{admin_id}' not found")

        team = Team.objects.create(name=name, description=description, admin=admin)
        return json.dumps({"id": str(team.id)})

    def list_teams(self) -> str:
        teams = Team.objects.select_related('admin').all().order_by('creation_time')
        result = [
            {
                "name": t.name,
                "description": t.description,
                "creation_time": t.creation_time.isoformat(),
                "admin": str(t.admin.id),
            }
            for t in teams
        ]
        return json.dumps(result)

    def describe_team(self, request: str) -> str:
        data = json.loads(request)
        team_id = data.get("id")
        try:
            t = Team.objects.select_related('admin').get(id=team_id)
        except Team.DoesNotExist:
            raise ValueError(f"Team '{team_id}' not found")
        return json.dumps(
            {
                "name": t.name,
                "description": t.description,
                "creation_time": t.creation_time.isoformat(),
                "admin": str(t.admin.id),
            }
        )

    def update_team(self, request: str) -> str:
        data = json.loads(request)
        team_id = data.get("id")
        updates = data.get("team", {})
        try:
            t = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise ValueError(f"Team '{team_id}' not found")

        name = updates.get("name", t.name)
        description = updates.get("description", t.description)
        admin_id = updates.get("admin")

        if len(name) > 64:
            raise ValueError("name can be max 64 characters")
        if len(description) > 128:
            raise ValueError("description can be max 128 characters")
        if name != t.name and Team.objects.filter(name=name).exists():
            raise ValueError(f"Team '{name}' already exists")

        t.name = name
        t.description = description
        if admin_id:
            try:
                t.admin = User.objects.get(id=admin_id)
            except User.DoesNotExist:
                raise ValueError(f"Admin user '{admin_id}' not found")
        t.save()
        return json.dumps({"id": str(t.id)})

    def add_users_to_team(self, request: str):
        data = json.loads(request)
        team_id = data.get("id")
        user_ids = data.get("users", [])

        if len(user_ids) > 50:
            raise ValueError("Cannot add more than 50 users at once")
        try:
            t = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise ValueError(f"Team '{team_id}' not found")

        if t.members.count() + len(user_ids) > 50:
            raise ValueError("Team cannot have more than 50 members")

        users = User.objects.filter(id__in=user_ids)
        found_ids = set(str(u.id) for u in users)
        missing = [uid for uid in user_ids if uid not in found_ids]
        if missing:
            raise ValueError(f"Users not found: {missing}")

        t.members.add(*users)
        return json.dumps({"message": "Users added successfully"})

    def remove_users_from_team(self, request: str):
        data = json.loads(request)
        team_id = data.get("id")
        user_ids = data.get("users", [])

        if len(user_ids) > 50:
            raise ValueError("Cannot remove more than 50 users at once")
        try:
            t = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise ValueError(f"Team '{team_id}' not found")

        users = User.objects.filter(id__in=user_ids)
        t.members.remove(*users)
        return json.dumps({"message": "Users removed successfully"})

    def list_team_users(self, request: str):
        data = json.loads(request)
        team_id = data.get("id")
        try:
            t = Team.objects.prefetch_related('members').get(id=team_id)
        except Team.DoesNotExist:
            raise ValueError(f"Team '{team_id}' not found")

        result = [
            {"id": str(u.id), "name": u.name, "display_name": u.display_name}
            for u in t.members.all()
        ]
        return json.dumps(result)
