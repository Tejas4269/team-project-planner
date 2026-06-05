import json
import os
from datetime import datetime, timezone

from django.utils import timezone as dj_timezone
from project_board_base import ProjectBoardBase
from teams.models import Team
from users.models import User
from .models import Board, Task

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT_DIR, exist_ok=True)


def _parse_dt(dt_str):
    """Parse an ISO datetime string or return now."""
    if not dt_str:
        return dj_timezone.now()
    try:
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return dj_timezone.now()


class BoardService(ProjectBoardBase):
    """Concrete implementation of ProjectBoardBase using Django ORM + SQLite."""

    def create_board(self, request: str) -> str:
        data = json.loads(request)
        name = data.get("name", "")
        description = data.get("description", "")
        team_id = data.get("team_id")
        creation_time = _parse_dt(data.get("creation_time"))

        if not name:
            raise ValueError("name is required")
        if len(name) > 64:
            raise ValueError("board name can be max 64 characters")
        if len(description) > 128:
            raise ValueError("description can be max 128 characters")

        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise ValueError(f"Team '{team_id}' not found")

        if Board.objects.filter(name=name, team=team).exists():
            raise ValueError(f"Board '{name}' already exists for this team")

        board = Board.objects.create(
            name=name, description=description, team=team, creation_time=creation_time
        )
        return json.dumps({"id": str(board.id)})

    def close_board(self, request: str) -> str:
        data = json.loads(request)
        board_id = data.get("id")
        try:
            board = Board.objects.prefetch_related('tasks').get(id=board_id)
        except Board.DoesNotExist:
            raise ValueError(f"Board '{board_id}' not found")

        if board.status == Board.Status.CLOSED:
            raise ValueError("Board is already closed")

        incomplete = board.tasks.exclude(status=Task.Status.COMPLETE).count()
        if incomplete > 0:
            raise ValueError(f"Cannot close board: {incomplete} task(s) are not COMPLETE")

        board.status = Board.Status.CLOSED
        board.end_time = dj_timezone.now()
        board.save()
        return json.dumps({"message": "Board closed successfully"})

    def add_task(self, request: str) -> str:
        data = json.loads(request)
        title = data.get("title", "")
        description = data.get("description", "")
        user_id = data.get("user_id")
        board_id = data.get("board_id")
        creation_time = _parse_dt(data.get("creation_time"))

        if not title:
            raise ValueError("title is required")
        if len(title) > 64:
            raise ValueError("title can be max 64 characters")
        if len(description) > 128:
            raise ValueError("description can be max 128 characters")

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise ValueError(f"Board '{board_id}' not found")

        if board.status != Board.Status.OPEN:
            raise ValueError("Can only add tasks to an OPEN board")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError(f"User '{user_id}' not found")

        if Task.objects.filter(title=title, board=board).exists():
            raise ValueError(f"Task '{title}' already exists on this board")

        task = Task.objects.create(
            title=title,
            description=description,
            board=board,
            assigned_user=user,
            creation_time=creation_time,
        )
        return json.dumps({"id": str(task.id)})

    def update_task_status(self, request: str):
        data = json.loads(request)
        task_id = data.get("id")
        status = data.get("status")

        valid_statuses = {s.value for s in Task.Status}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise ValueError(f"Task '{task_id}' not found")

        task.status = status
        task.save()
        return json.dumps({"id": str(task.id), "status": task.status})

    def list_boards(self, request: str) -> str:
        data = json.loads(request)
        team_id = data.get("id")
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise ValueError(f"Team '{team_id}' not found")

        boards = Board.objects.filter(team=team, status=Board.Status.OPEN)
        result = [{"id": str(b.id), "name": b.name} for b in boards]
        return json.dumps(result)

    def export_board(self, request: str) -> str:
        data = json.loads(request)
        board_id = data.get("id")
        try:
            board = Board.objects.select_related('team').prefetch_related(
                'tasks__assigned_user'
            ).get(id=board_id)
        except Board.DoesNotExist:
            raise ValueError(f"Board '{board_id}' not found")

        tasks = board.tasks.all().order_by('status', 'creation_time')
        status_counts = {"OPEN": 0, "IN_PROGRESS": 0, "COMPLETE": 0}
        for t in tasks:
            status_counts[t.status] += 1

        lines = []
        lines.append("=" * 70)
        lines.append(f"  PROJECT BOARD: {board.name.upper()}")
        lines.append("=" * 70)
        lines.append(f"  Team        : {board.team.name}")
        lines.append(f"  Status      : {board.status}")
        lines.append(f"  Description : {board.description or '—'}")
        lines.append(f"  Created     : {board.creation_time.strftime('%Y-%m-%d %H:%M UTC')}")
        if board.end_time:
            lines.append(f"  Closed      : {board.end_time.strftime('%Y-%m-%d %H:%M UTC')}")
        lines.append("")
        lines.append(f"  Tasks Summary  |  Open: {status_counts['OPEN']}  "
                     f"In Progress: {status_counts['IN_PROGRESS']}  "
                     f"Complete: {status_counts['COMPLETE']}  "
                     f"Total: {tasks.count()}")
        lines.append("-" * 70)

        STATUS_ICON = {"OPEN": "○", "IN_PROGRESS": "◑", "COMPLETE": "●"}

        for task in tasks:
            icon = STATUS_ICON.get(task.status, "?")
            lines.append(f"  {icon}  [{task.status:<11}]  {task.title}")
            lines.append(f"       Assigned : {task.assigned_user.display_name} (@{task.assigned_user.name})")
            if task.description:
                lines.append(f"       Note     : {task.description}")
            lines.append(f"       Created  : {task.creation_time.strftime('%Y-%m-%d %H:%M UTC')}")
            lines.append("")

        lines.append("=" * 70)

        filename = f"board_{board.id}.txt"
        filepath = os.path.join(OUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return json.dumps({"out_file": filename})
