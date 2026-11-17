"""Streamlit demo: personalising / simplifying text with an LLM.

Run with:  streamlit run run_lfm3.py
"""
import html

import streamlit as st
import torch
from transformers import pipeline

MODEL_NAME = "LiquidAI/LFM3-1.7B"

EXAMPLE_TEXTS = {
    "Beispiel 1 – Nachrichten": "Sport und Bewegung gehören für viele Kinder und Jugendliche nicht mehr zum Alltag. Nur 14 Prozent bewegen sich laut WHO täglich für eine Stunde mäßig bis intensiv. Auch in Deutschland gibt es viele Bewegungsmuffel. ",
    "Beispiel 2 – Wikipedia": "Lego Creator ist ein Lego-Computerspiel aus dem Jahr 1998. Das Spiel wurde von Superscape entwickelt und legt den Fokus darauf, Szenerien aus Legosteinen und Minifiguren zu bauen.",
    "Beispiel 3 – Gesundheitsinformationen": "Die echte Grippe ist eine ernstzunehmende Infektionskrankheit. Besonders bei älteren Menschen kann sie einen schweren Verlauf nehmen und sogar tödlich enden. Deshalb raten Fachleute allen Risikogruppen zur Grippeimpfung.",
}

OWN_TEXT = "Eigener Text"

STRATEGIES = {
    "Einfache Sprache": "Vereinfache den folgenden Text in Einfache Sprache.",
    "Leichte Sprache": "Vereinfache den folgenden Text in Leichte Sprache für Menschen mit Lernbehinderungen.",
    "Kind": "Schreibe den folgenden Text für ein 5-jähriges Kind um.",
    "Anderes": None,  # instruction is entered by the user
}

BACKGROUNDS = {
    "Keiner": None,
    "Schüler*in": "Die Person geht zur Schule.",
    "Interessiert an Medizin": "Die Person hat großes Interesse an Medizin.",
    "Lernt gerade Deutsch": "Die Person hat eine andere Muttersprache als Deutsch. Der Text soll trotzdem auf Deutsch sein.",
    "Renter": "Die Person ist bereits in Rente.",
    "Anderes": None,  # entered by the user
}

GENDERS = {
    "keine Angabe": None,
    "Weiblich": "weiblich",
    "Männlich": "männlich",
    "Divers": "divers",
}


@st.cache_resource(show_spinner="Lade die KI …")
def load_generator():
    return pipeline(
        "text-generation",
        model=MODEL_NAME,
        trust_remote_code=True,
        device="cuda" if torch.cuda.is_available() else "cpu",
    )


def build_prompt(text, strategy_instruction, background, gender):
    """Assemble the prompt from the user's selections."""
    parts = [strategy_instruction.strip()]

    reader = []
    if background:
        reader.append(background.strip())
    if gender:
        reader.append(f"Das Geschlecht der Person ist {gender}.")
    if reader:
        parts.append(
            "Passe den Text an die folgende Person an:\n" + "\n".join(f"- {r}" for r in reader)
        )

    parts.append("Gib nur den umgeschriebenen Text aus.")
    parts.append(f"Text:\n{text.strip()}")
    return "\n\n".join(parts)


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


# --------------------------------------------------------------------------- UI
st.set_page_config(page_title="LLM Text Personalisierung", layout="wide")
st.title("Wie LLMs Texte personalisieren können")

# --- Sidebar: personalisation options ---
with st.sidebar:
    st.header("Level der Vereinfachung")
    strategy = st.radio("Strategy", list(STRATEGIES), label_visibility="collapsed")
    if strategy == "Anderes":
        strategy_instruction = st.text_area(
            "Custom instruction",
            value="Schreibe den folgenden Text um, sodass er ",
        )
    else:
        strategy_instruction = STRATEGIES[strategy]

    st.header("Profil des Lesers")
    background_choice = st.selectbox("Hintergrund", list(BACKGROUNDS))
    if background_choice == "Anderes":
        background = st.text_input("Beschreibe den Hintergrund", value="Die Person ")
    else:
        background = BACKGROUNDS[background_choice]

    gender_choice = st.selectbox("Geschlecht", list(GENDERS))
    gender = GENDERS[gender_choice]

# --- Main area: input text, prompt, output ---
col_in, col_out = st.columns(2)

with col_in:
    st.subheader("Eingabetext")
    source = st.selectbox("Text source", [OWN_TEXT, *EXAMPLE_TEXTS], index=1)
    if source == OWN_TEXT:
        input_text = st.text_area("Schwerer Text", height=200)
    else:
        input_text = st.text_area(
            "Schwerer Text", value=EXAMPLE_TEXTS[source], height=200, key=f"text_{source}"
        )

    prompt = build_prompt(input_text, strategy_instruction, background, gender)
    # st.subheader("Resulting prompt")
    # st.caption("This prompt updates live with your selections in the sidebar.")
    # st.code(prompt, language=None, wrap_lines=True)

with col_out:
    st.subheader("Vom Modell vereinfachter Text")
    if st.button("Generate", type="primary", disabled=not input_text.strip()):
        with st.spinner("Generiert den Text …"):
            new_result = generate(prompt, 0.1, 2048)
        # Move the previous output into the history (newest first)
        if "result" in st.session_state:
            st.session_state.setdefault("history", []).insert(
                0,
                {
                    "label": st.session_state["result_label"],
                    "text": st.session_state["result"],
                    "prompt": st.session_state["result_prompt"],
                },
            )
        st.session_state["result"] = new_result
        st.session_state["result_prompt"] = prompt
        st.session_state["result_label"] = f"{strategy} · {background_choice} · {gender_choice}"

    if "result" in st.session_state:
        st.markdown(st.session_state["result"])
        with st.expander(":gray[Verwendeter Prompt]"):
            st.code(st.session_state["result_prompt"], language=None, wrap_lines=True)
        if st.session_state["result_prompt"] != prompt:
            st.info("Die Konfiguration hat sich geändert – klicke *Generate* um die Änderungen anzuwenden.")

    if st.session_state.get("history"):
        st.divider()
        st.markdown(":gray[**Verlauf**]")
        for i, entry in enumerate(st.session_state["history"]):
            with st.expander(f":gray[{len(st.session_state['history']) - i}. {entry['label']}]"):
                st.markdown(
                    f"<div style='color: grey; white-space: pre-wrap;'>{html.escape(entry['text'])}</div>",
                    unsafe_allow_html=True,
                )
                if "prompt" in entry:
                    st.caption("Verwendeter Prompt:")
                    st.code(entry["prompt"], language=None, wrap_lines=True)
