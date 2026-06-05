# Team Project Planner

A Django-based REST API tool for managing users, teams, and project boards with tasks.

---

## Tech Stack & Choices

| Concern | Choice | Rationale |
|---|---|---|
| Framework | Django + Django REST Framework | Required per spec; DRF provides clean view/URL routing |
| Persistence | SQLite via Django ORM | Single-file local storage; lives in `db/planner.db` |
| ID strategy | UUID4 | Collision-free, no sequential ID leakage |
| Timestamps | UTC with ISO 8601 | Unambiguous, universally parseable format |

---

## Project Structure

```
planner/               # Django project config (settings, root urls)
users/                 # User management app
teams/                 # Team management app
boards/                # Board & task management app
db/                    # SQLite database (auto-created on migrate, excluded from repo)
out/                   # Exported board .txt files (auto-created on export)
user_base.py           # Provided abstract base class
team_base.py           # Provided abstract base class
project_board_base.py  # Provided abstract base class
```

Each app follows a consistent pattern:
```
models.py   → defines the data model
service.py  → concrete implementation of the base class
views.py    → Django views wrapping the service
urls.py     → URL routing
```

---

## Setup & Run

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the db folder (first time only)
mkdir db

# 4. Run migrations
python manage.py migrate

# 5. Start the server
python manage.py runserver
```

Server runs at `http://127.0.0.1:8000`

---

## API Reference

### Users

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/users/create/` | Create user |
| GET | `/api/users/` | List all users |
| GET | `/api/users/<id>/` | Describe user |
| PATCH | `/api/users/<id>/` | Update display_name only |
| GET | `/api/users/<id>/teams/` | Get teams user belongs to |

**Create user request:**
```json
{ "name": "john_doe", "display_name": "John Doe" }
```

### Teams

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/teams/create/` | Create team |
| GET | `/api/teams/` | List all teams |
| GET | `/api/teams/<id>/` | Describe team |
| PATCH | `/api/teams/<id>/` | Update team |
| GET | `/api/teams/<id>/users/` | List team members |
| POST | `/api/teams/<id>/users/` | Add users `{ "users": ["<id>"] }` |
| POST | `/api/teams/<id>/users/?action=remove` | Remove users |

### Boards & Tasks

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/boards/create/` | Create board for a team |
| GET | `/api/boards/team/<team_id>/` | List OPEN boards for a team |
| POST | `/api/boards/<id>/close/` | Close board (all tasks must be COMPLETE) |
| POST | `/api/boards/<id>/tasks/add/` | Add task to an OPEN board |
| PATCH | `/api/boards/tasks/<task_id>/status/` | Update task status |
| GET | `/api/boards/<id>/export/` | Export board as `.txt` to `out/` folder |

Task status values: `OPEN` → `IN_PROGRESS` → `COMPLETE`

---

## Constraints Enforced

- User name must be unique; max 64 chars; immutable after creation
- Team name must be unique; max 64 chars; max 50 members
- Board name must be unique per team; max 64 chars
- Task title must be unique per board; max 64 chars
- Board cannot be closed unless all tasks are `COMPLETE`
- Tasks cannot be added to a `CLOSED` board
- All descriptions max 128 chars

---

## Assumptions

- `board_id` is passed via the URL route when adding tasks (the base class docstring field label says "team id" but contextually refers to the board)
- `list_boards` returns only `OPEN` boards — the method name implies active/in-progress boards
- Admin user is not auto-added to team members; admin and membership are separate concerns
- `out/` folder for board exports is auto-created if it doesn't exist
- All invalid inputs raise `ValueError` and return a `400` response with an `error` message
