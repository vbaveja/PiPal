import json
from pathlib import Path


def get_repo_root() -> Path:
    """Return the project root so helper functions can build paths."""
    return Path(__file__).resolve().parents[1]


def create_user(username: str) -> Path:
    """Create a student workspace folder and its projects directory."""
    user_dir = get_repo_root() / "users" / username
    projects_dir = user_dir / "projects"

    # Make sure the base student folder exists without duplicating structure.
    user_dir.mkdir(parents=True, exist_ok=True)
    projects_dir.mkdir(parents=True, exist_ok=True)

    return user_dir


def get_user_projects_dir(username: str) -> Path:
    """Return the projects directory for a student workspace."""
    return create_user(username) / "projects"


def get_project_dir(username: str, project_name: str) -> Path:
    """Return the project folder path for a student project."""
    return get_user_projects_dir(username) / project_name


def get_project_file(username: str, project_name: str, filename: str) -> Path:
    """Return a project file path, creating parent folders if needed."""
    project_dir = get_project_dir(username, project_name)
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir / filename


def create_project(username: str, project_name: str) -> Path:
    """Create a project folder under users/<student>/projects/ and its starter files."""
    user_dir = create_user(username)
    projects_dir = get_user_projects_dir(username)
    project_dir = projects_dir / project_name

    # Keep the student project structure nested and easy to browse.
    user_dir.mkdir(parents=True, exist_ok=True)
    projects_dir.mkdir(parents=True, exist_ok=True)
    project_dir.mkdir(parents=True, exist_ok=True)

    # Each project keeps its own memory, code, wiring, chat, and learn files.
    memory_path = project_dir / "memory.json"
    code_path = project_dir / "code.py"
    wiring_path = project_dir / "wiring.json"
    chat_path = project_dir / "chat_history.json"
    learn_path = project_dir / "learn.json"

    if not memory_path.exists():
        memory_path.write_text(json.dumps({}, indent=2))

    if not code_path.exists():
        code_path.write_text("")

    if not wiring_path.exists():
        wiring_path.write_text(json.dumps({}, indent=2))

    if not chat_path.exists():
        chat_path.write_text(json.dumps([], indent=2))

    if not learn_path.exists():
        learn_path.write_text(json.dumps({}, indent=2))

    return project_dir


def load_project_memory(username: str, project_name: str) -> dict:
    """Load a project's memory file as a Python dictionary."""
    project_dir = get_user_projects_dir(username) / project_name
    memory_path = project_dir / "memory.json"

    if not memory_path.exists():
        raise FileNotFoundError(f"Memory file not found: {memory_path}")

    return json.loads(memory_path.read_text())


def save_project_memory(username: str, project_name: str, memory: dict) -> Path:
    """Save project memory back to memory.json and return the file path."""
    project_dir = create_project(username, project_name)
    memory_path = project_dir / "memory.json"
    memory_path.write_text(json.dumps(memory, indent=2))
    return memory_path


def load_code(username: str, project_name: str, default_code: str = "") -> str:
    """Load project code from code.py, creating it if missing."""
    code_path = get_project_file(username, project_name, "code.py")
    if not code_path.exists() or code_path.read_text() == "":
        if default_code:
            code_path.write_text(default_code)
        return default_code
    return code_path.read_text()


def save_code(username: str, project_name: str, code: str) -> Path:
    """Save code into the project's code.py file."""
    code_path = get_project_file(username, project_name, "code.py")
    code_path.write_text(code)
    return code_path


def load_wiring(username: str, project_name: str) -> dict:
    """Load wiring configuration for the project."""
    wiring_path = get_project_file(username, project_name, "wiring.json")
    if not wiring_path.exists():
        wiring_path.write_text(json.dumps({}, indent=2))
    return json.loads(wiring_path.read_text())


def save_wiring(username: str, project_name: str, wiring: dict) -> Path:
    """Save wiring configuration for the project."""
    wiring_path = get_project_file(username, project_name, "wiring.json")
    wiring_path.write_text(json.dumps(wiring, indent=2))
    return wiring_path


def load_chat_history(username: str, project_name: str) -> list:
    """Load saved chat history for the project."""
    history_path = get_project_file(username, project_name, "chat_history.json")
    if not history_path.exists():
        history_path.write_text(json.dumps([], indent=2))
    return json.loads(history_path.read_text())


def save_chat_history(username: str, project_name: str, chat_history: list) -> Path:
    """Save chat history for the project."""
    history_path = get_project_file(username, project_name, "chat_history.json")
    history_path.write_text(json.dumps(chat_history, indent=2))
    return history_path


def load_learn_data(username: str, project_name: str) -> dict:
    """Load learning-related data for the project."""
    learn_path = get_project_file(username, project_name, "learn.json")
    if not learn_path.exists():
        learn_path.write_text(json.dumps({}, indent=2))
    return json.loads(learn_path.read_text())


def save_learn_data(username: str, project_name: str, learn_data: dict) -> Path:
    """Save learning-related data for the project."""
    learn_path = get_project_file(username, project_name, "learn.json")
    learn_path.write_text(json.dumps(learn_data, indent=2))
    return learn_path
