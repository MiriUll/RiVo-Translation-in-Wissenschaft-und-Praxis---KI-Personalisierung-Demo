from groq import Groq
import streamlit as st

@st.cache_resource(show_spinner="Lade die KI …")
def load_client(api_key):
    client = Groq(
        api_key=api_key
    )
    return client

def generate(prompt, temperature, max_new_tokens, api_key):
    cli = load_client(api_key)

    chat_completion = cli.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="openai/gpt-oss-120b",
        temperature=temperature,
        max_completion_tokens=max_new_tokens,
    )

    return chat_completion.choices[0].message.content