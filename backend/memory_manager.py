import json
from pathlib import Path


DEFAULT_MEMORY = {
    "student_level": "Beginner",
    "hardware_used": [],
    "gpio_assignments": {},
    "current_learning_goal": "",
    "completed_steps": [],
    "current_focus": "",
}


def get_repo_root() -> Path:
    """Return the repository root so memory files can be stored under users/."""
    return Path(__file__).resolve().parents[1]


def get_project_memory_path(username: str, project_name: str) -> Path:
    """Build the memory.json path under users/<student>/projects/<project>."""
    return get_repo_root() / "users" / username / "projects" / project_name / "memory.json"


def ensure_project_memory(username: str, project_name: str) -> Path:
    """Create the project folder and memory.json if they do not exist."""
    memory_path = get_project_memory_path(username, project_name)
    memory_path.parent.mkdir(parents=True, exist_ok=True)

    if not memory_path.exists():
        memory_path.write_text(json.dumps(DEFAULT_MEMORY, indent=2))

    return memory_path


def load_project_memory(username: str, project_name: str) -> dict:
    """Load memory.json for a project and create it if missing."""
    memory_path = ensure_project_memory(username, project_name)
    return json.loads(memory_path.read_text())


def save_project_memory(username: str, project_name: str, memory: dict) -> Path:
    """Save memory data back into a project's memory.json file."""
    memory_path = ensure_project_memory(username, project_name)
    memory_path.write_text(json.dumps(memory, indent=2))
    return memory_path


def update_memory_field(username: str, project_name: str, field: str, value) -> dict:
    """Update a single memory field and save the result."""
    memory = load_project_memory(username, project_name)
    memory[field] = value
    save_project_memory(username, project_name, memory)
    return memory


def append_completed_step(username: str, project_name: str, step: str) -> dict:
    """Add a completed step to the project memory."""
    memory = load_project_memory(username, project_name)
    memory["completed_steps"].append(step)
    save_project_memory(username, project_name, memory)
    return memory


def add_hardware_used(username: str, project_name: str, hardware_item: str) -> dict:
    """Track hardware used in the project."""
    memory = load_project_memory(username, project_name)
    if hardware_item not in memory["hardware_used"]:
        memory["hardware_used"].append(hardware_item)
    save_project_memory(username, project_name, memory)
    return memory


def set_gpio_assignment(username: str, project_name: str, pin: str, component: str) -> dict:
    """Store a GPIO pin assignment for the project."""
    memory = load_project_memory(username, project_name)
    memory["gpio_assignments"][pin] = component
    save_project_memory(username, project_name, memory)
    return memory
