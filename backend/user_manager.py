import json
from pathlib import Path
from typing import List, Optional


def get_repo_root() -> Path:
    """Return the repository root so helper functions can build paths."""
    return Path(__file__).resolve().parents[1]


def get_user_db_path() -> Path:
    """Return the path for the simple file-based user database."""
    return get_repo_root() / "user_db.json"


def load_user_db() -> dict:
    """Load the user database from disk, creating defaults if needed."""
    db_path = get_user_db_path()
    if not db_path.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db_path.write_text(json.dumps({
            "admin": {"password": "pipal-admin", "role": "admin"},
            "student": {"password": "student", "role": "student", "level": "beginner"}
        }, indent=2))
    return json.loads(db_path.read_text())


def save_user_db(user_db: dict) -> Path:
    """Save the user database back to disk."""
    db_path = get_user_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.write_text(json.dumps(user_db, indent=2))
    return db_path


def ensure_user_db() -> dict:
    """Ensure the user database exists and return its content."""
    return load_user_db()


def verify_user(username: str, password: str) -> Optional[dict]:
    """Check username and password against the local user database."""
    users = load_user_db()
    user = users.get(username)
    if not user:
        return None
    if user.get("password") != password:
        return None
    return user


def create_user_account(
    username: str,
    password: str,
    role: str = "student",
    level: str = "beginner",
) -> dict:
    """Create a new user account in the local user database."""
    users = load_user_db()
    if username in users:
        raise ValueError(f"User already exists: {username}")
    if role not in {"admin", "student"}:
        raise ValueError("Role must be 'admin' or 'student'.")
    new_user = {"password": password, "role": role}
    if role == "student":
        new_user["level"] = level
    users[username] = new_user
    save_user_db(users)
    return users[username]


def list_students() -> List[str]:
    """Return a sorted list of student usernames from the user database."""
    users = load_user_db()
    return sorted([name for name, info in users.items() if info.get("role") == "student"])


def list_users() -> dict:
    """Return the full user database."""
    return load_user_db()
