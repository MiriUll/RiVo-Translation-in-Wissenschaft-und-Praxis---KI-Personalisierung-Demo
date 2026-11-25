"""Streamlit demo: personalising / simplifying text with an LLM.

Run with:  streamlit run run_demo.py
"""
import html

import streamlit as st
from personalized_prompt import *
from api_provider import *

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

    interest_choice = st.selectbox("Interessen", list(INTERESTS))
    if interest_choice == "Anderes":
        interest = st.text_input("Beschreibe die Interessen", value="Die Person interessiert sich für ")
    else:
        interest = INTERESTS[interest_choice]

    difficulty_choices = st.multiselect("Was fällt der Person schwer?", list(DIFFICULTIES))
    difficulties = [DIFFICULTIES[d] for d in difficulty_choices]

    goal_choice = st.selectbox("Ziel beim Lesen", list(GOALS))
    goal = GOALS[goal_choice]

    gender_choice = st.selectbox("Geschlecht", list(GENDERS))
    gender = GENDERS[gender_choice]

# --- Main area: input text, prompt, output ---
col_in, col_out = st.columns(2)

with col_in:
    st.subheader("API Key")
    api_key = st.text_input("Erstelle dir einen Account unter [https://console.groq.com/keys](https://console.groq.com/keys) und füge den API Key hier ein. ",  type="password")
    st.subheader("Eingabetext")
    source = st.selectbox("Text source", [OWN_TEXT, *EXAMPLE_TEXTS], index=1)
    if source == OWN_TEXT:
        input_text = st.text_area("Schwerer Text", height=200)
    else:
        input_text = st.text_area(
            "Schwerer Text", value=EXAMPLE_TEXTS[source], height=200, key=f"text_{source}"
        )

    prompt = build_prompt(input_text, strategy_instruction, background, interest,
                          difficulties, goal, gender)
    # st.subheader("Resulting prompt")
    # st.caption("This prompt updates live with your selections in the sidebar.")
    # st.code(prompt, language=None, wrap_lines=True)

with col_out:
    st.subheader("Vom Modell vereinfachter Text")
    if st.button("Generate", type="primary", disabled=not input_text.strip()):
        with st.spinner("Generiert den Text …"):
            new_result = generate(prompt, 0.0, 2048, api_key=api_key)
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
        profile = [background_choice, interest_choice, *difficulty_choices, goal_choice, gender_choice]
        profile = [p for p in profile if p not in ("Keiner", "Keine Angabe", "keine Angabe")]
        st.session_state["result_label"] = " · ".join([strategy, *profile])

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
