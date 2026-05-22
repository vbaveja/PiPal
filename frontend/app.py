import json
import os
import sys
from openai import OpenAI
import streamlit as st

# Ensure the repository root is on sys.path so backend imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("PiPal")

st.subheader("Your AI Raspberry Pi Learning Companion")

student_skill_level = "Beginner"

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Read the current project code once and keep it in session state so the
# assistant can improve it step by step in the chat.
with open(os.path.join(repo_root, "projects", "blink_led.py"), "r") as file:
    default_code = file.read()

if "current_code" not in st.session_state:
    st.session_state.current_code = default_code

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Read the PiPal agent rules and project context for the prompt.
with open(os.path.join(repo_root, "AGENTS.md"), "r") as file:
    agent_rules = file.read()

with open(os.path.join(repo_root, "project_context.json"), "r") as file:
    project_context = json.load(file)

system_prompt = (
    "You are PiPal, an educational Raspberry Pi coding assistant for kids. "
    "Use friendly, beginner-safe Raspberry Pi guidance and prefer gpiozero-style hardware code. "
    "Keep your explanations simple, add comments, and stay focused on safe code changes.\n\n"
    f"Student skill level: {student_skill_level}\n\n"
    f"Project context:\n{json.dumps(project_context, indent=2)}\n\n"
    f"Agent rules:\n{agent_rules}"
)


def extract_modified_code(response_text: str):
    """Extract the updated code from the assistant response when it is included."""
    if "MODIFIED CODE:" not in response_text:
        return None

    code_block = response_text.split("MODIFIED CODE:", 1)[1]

    if "EXPLANATION:" in code_block:
        code_block = code_block.split("EXPLANATION:", 1)[0]

    code_block = code_block.strip()

    if code_block.startswith("```"):
        code_block = code_block.strip("`")
        if "\n" in code_block:
            code_block = code_block.split("\n", 1)[1]
        code_block = code_block.rsplit("```", 1)[0].strip()

    return code_block or None


st.write("Ask PiPal to change the code, and I will update the code in this chat.")

st.code(st.session_state.current_code, language="python")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_message = st.chat_input("What would you like to change in the project?")

if user_message:
    prompt = (
        "Here is the current project code:\n"
        f"{st.session_state.current_code}\n\n"
        "Student request:\n"
        f"{user_message}\n\n"
        "Please update the code safely, keep it beginner friendly, add comments, "
        "and explain what changed simply."
    )

    st.session_state.chat_history.append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(st.session_state.chat_history)
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    assistant_reply = response.choices[0].message.content
    updated_code = extract_modified_code(assistant_reply)

    if updated_code:
        st.session_state.current_code = updated_code

    st.session_state.chat_history.append(
        {"role": "assistant", "content": assistant_reply}
    )

    st.rerun()
