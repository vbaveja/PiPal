from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def get_repo_root() -> Path:
    """Return the repository root for this project."""
    return Path(__file__).resolve().parents[1]


def read_text_file(path: Path) -> str:
    """Read a text file and return its contents."""
    return path.read_text()


def load_json_file(path: Path):
    """Load a JSON file and return the parsed data."""
    return json.loads(read_text_file(path))


def load_agents_rules(repo_root: Optional[Path] = None) -> str:
    """Load the AGENTS.md file used to guide PiPal's tone and behavior."""
    root = repo_root or get_repo_root()
    return read_text_file(root / "AGENTS.md")


def load_project_context(repo_root: Optional[Path] = None) -> dict:
    """Load the learner-facing project context settings."""
    root = repo_root or get_repo_root()
    return load_json_file(root / "project_context.json")


def load_hardware_components(repo_root: Optional[Path] = None) -> dict:
    """Load the hardware component descriptions."""
    root = repo_root or get_repo_root()
    return load_json_file(root / "hardware" / "components.json")


def load_pin_reference(repo_root: Optional[Path] = None) -> dict:
    """Load the GPIO pin reference data."""
    root = repo_root or get_repo_root()
    return load_json_file(root / "hardware" / "pin_reference.json")


def load_wiring_rules(repo_root: Optional[Path] = None) -> dict:
    """Load the wiring rules for beginner-safe hardware guidance."""
    root = repo_root or get_repo_root()
    return load_json_file(root / "hardware" / "wiring_rules.json")


def load_all_context(repo_root: Optional[Path] = None) -> dict:
    """Load every project context file into one reusable dictionary."""
    root = repo_root or get_repo_root()

    return {
        "agent_rules": load_agents_rules(root),
        "project_context": load_project_context(root),
        "hardware_components": load_hardware_components(root),
        "pin_reference": load_pin_reference(root),
        "wiring_rules": load_wiring_rules(root),
    }


def format_context_for_prompt(context: dict) -> str:
    """Convert the loaded context into a readable prompt section."""
    return (
        f"Agent rules:\n{context['agent_rules']}\n\n"
        f"Project context:\n{json.dumps(context['project_context'], indent=2)}\n\n"
        f"Hardware components:\n{json.dumps(context['hardware_components'], indent=2)}\n\n"
        f"Pin reference:\n{json.dumps(context['pin_reference'], indent=2)}\n\n"
        f"Wiring rules:\n{json.dumps(context['wiring_rules'], indent=2)}"
    )
