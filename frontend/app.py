import os
from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("PiPal")

st.subheader("Your AI Raspberry Pi Learning Companion")

user_request = st.text_input(
    "What would you like to change in the project?"
)

# Determine the repo root relative to this app file.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Read existing project code
with open(os.path.join(repo_root, "projects", "blink_led.py"), "r") as file:
    current_code = file.read()

# Read the PiPal agent rules and include them in the prompt context.
with open(os.path.join(repo_root, "AGENTS.md"), "r") as file:
    agent_rules = file.read()

st.code(current_code, language="python")

if st.button("Generate Code Change"):

    prompt = f"""
    You are PiPal, an educational Raspberry Pi coding assistant for kids.

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

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are PiPal."},
            {"role": "user", "content": prompt}
        ]
    )

    st.write(response.choices[0].message.content)