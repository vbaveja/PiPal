"""Build the OpenAI prompt messages used by PiPal."""

from __future__ import annotations

import json
from typing import Optional

from backend.context_loader import format_context_for_prompt, load_all_context


def format_project_memory_for_prompt(project_memory: Optional[dict]) -> str:
    """Turn project memory into a readable prompt section."""
    if not project_memory:
        return "Project memory:\nNo project memory saved yet."

    return (
        "Project memory:\n"
        f"{json.dumps(project_memory, indent=2)}"
    )


def build_system_message(
    student_skill_level: str,
    prompt_context: str,
    project_memory: Optional[dict] = None,
) -> str:
    """Create the system prompt for PiPal."""
    project_memory_section = format_project_memory_for_prompt(project_memory)

    return (
        "You are PiPal, a beginner-friendly Raspberry Pi assistant.\n"
        "Keep explanations simple, build safe code, and teach step by step.\n"
        "Use project memory, hardware context, AGENTS.md guidance, and the current code\n"
        "to make thoughtful beginner-friendly changes.\n\n"
        f"Student skill level: {student_skill_level}\n\n"
        f"{project_memory_section}\n\n"
        f"{prompt_context}"
    )


def build_user_message(current_code: str, user_request: str) -> str:
    """Create the user prompt for the current code change request."""
    return (
        "Update this project code using the saved project memory, hardware context,\n"
        "and beginner-friendly teaching style.\n\n"
        f"Current project code:\n{current_code}\n\n"
        f"Student request:\n{user_request}\n\n"
        "Return only:\n"
        "MODIFIED CODE:\n"
        "...\n\n"
        "EXPLANATION:\n"
        "..."
    )


def build_prompt(
    current_code: str,
    user_request: str,
    student_skill_level: str,
    repo_root,
    project_memory: Optional[dict] = None,
    username: Optional[str] = None,
    project_name: Optional[str] = None,
):
    """Create the system and user messages for the AI request."""
    if project_memory is None and username and project_name:
        from backend.memory_manager import load_project_memory

        try:
            project_memory = load_project_memory(username, project_name)
        except FileNotFoundError:
            project_memory = None

    context_data = load_all_context(repo_root)
    prompt_context = format_context_for_prompt(context_data)

    return [
        {
            "role": "system",
            "content": build_system_message(
                student_skill_level,
                prompt_context,
                project_memory,
            ),
        },
        {
            "role": "user",
            "content": build_user_message(current_code, user_request),
        },
    ]
