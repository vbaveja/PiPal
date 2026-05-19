import os
from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("PiPal")

st.subheader("Your AI Raspberry Pi Learning Companion")

user_request = st.text_input(
    "What would you like your Raspberry Pi project to do?"
)

if st.button("Generate Idea"):

    prompt = f"""
    You are PiPal, an educational Raspberry Pi assistant for kids.

    The student request is:
    {user_request}

    Explain simply how this could work using Raspberry Pi.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are PiPal."},
            {"role": "user", "content": prompt}
        ]
    )

    st.write(response.choices[0].message.content)
    