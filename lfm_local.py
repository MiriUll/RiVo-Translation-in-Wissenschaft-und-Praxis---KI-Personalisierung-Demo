import torch
from transformers import pipeline
import streamlit as st

MODEL_NAME = "LiquidAI/LFM3-1.7B"

@st.cache_resource(show_spinner="Lade die KI …")
def load_generator():
    return pipeline(
        "text-generation",
        model=MODEL_NAME,
        trust_remote_code=True,
        device="cuda" if torch.cuda.is_available() else "cpu",
    )

def extract_answer(generated):
    """Get the assistant's answer from the pipeline output.

    Depending on the transformers version / chat template, the reply is a plain
    string, a message dict with "content" as string or list of blocks, or a
    message without "content" (e.g. only reasoning, if the answer was cut off).
    """
    if isinstance(generated, str):
        return generated
    message = generated[-1]
    if isinstance(message, str):
        return message

    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):  # e.g. [{"type": "text", "text": "..."}]
        return "".join(
            block.get("text", "") if isinstance(block, dict) else str(block) for block in content
        )

    # No answer found -> show what the model actually returned
    st.error("Die Antwort des Modells hat kein erwartetes Format. Rohdaten:")
    st.json(message)
    st.stop()


def generate(prompt, temperature, max_new_tokens):
    generator = load_generator()
    messages = [{"role": "user", "content": prompt}]
    output = generator(
        messages,
        do_sample=True,
        temperature=temperature,
        top_k=50,
        repetition_penalty=1.1,
        max_new_tokens=max_new_tokens,
    )
    return extract_answer(output[0]["generated_text"])