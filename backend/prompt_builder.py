"""Build the OpenAI prompt messages used by PiPal."""


def build_prompt(current_code: str, user_request: str, student_skill_level: str, agent_rules: str):
    """Create the system/user chat messages for the AI request."""
    system_message = (
        "You are PiPal. "
        "Use friendly, beginner-safe Raspberry Pi guidance and prefer gpiozero-style hardware code. "
        "Load the agent rules below to shape your teaching tone and behavior.\n\n"
        f"{agent_rules}"
    )

    user_message = f"""
You are PiPal, an educational Raspberry Pi coding assistant for kids.
Student skill level: {student_skill_level}

Here is the student's current project:

{current_code}

Student request:
{user_request}

Your tasks:
1. Modify the code safely
2. Keep it beginner friendly
3. Add comments
4. Explain what changed simply

Return:
MODIFIED CODE:
...

EXPLANATION:
...
"""

    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]
