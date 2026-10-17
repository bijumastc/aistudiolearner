"""Rubric feedback assistant — starter template.
Run: streamlit run rubric_feedback.py
Ideas: batch-upload answers from a CSV, save teacher edits, compare two models' marks for consistency.
"""
import json

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Rubric Feedback", page_icon="🧾")

# ---- AI helper: works with Groq, Gemini, Mistral, OpenRouter, Hugging Face (change BASE_URL + MODEL) ----
BASE_URL = "https://api.groq.com/openai/v1"
MODEL = st.secrets.get("MODEL", "openai/gpt-oss-20b")      # check console.groq.com/docs/models for current names


def ask(messages, temperature=0.3, json_mode=False):
    payload = {"model": MODEL, "messages": messages, "temperature": temperature, "max_tokens": 3000}
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    r = requests.post(f"{BASE_URL}/chat/completions", json=payload, timeout=90,
                      headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"})
    if r.status_code != 200:
        st.error(f"API error {r.status_code}: {r.text[:300]}")
        st.stop()
    return r.json()["choices"][0]["message"]["content"]

st.title("🧾 Rubric Feedback Assistant")
question = st.text_input("Question", "Explain the water cycle. (5 marks)")
rubric = st.text_area("Rubric (one per line)", "Names the stages (2)\nExplains each stage (2)\nUses a diagram or example (1)")
answer = st.text_area("Student answer (anonymised)", height=150)

if st.button("Get feedback", type="primary") and answer:
    raw = ask([
        {"role": "system", "content": "You are a fair examiner giving formative feedback. Output only JSON."},
        {"role": "user", "content": f"Question: {question}\nRubric:\n{rubric}\nAnswer:\n{answer}\n"
         'JSON: {"criteria":[{"criterion":"","max":0,"awarded":0,"comment":""}],"overall":"","next_step":""}'},
    ], temperature=0.1, json_mode=True)
    st.session_state.fb = json.loads(raw)

if "fb" in st.session_state:
    fb = st.session_state.fb
    table = st.data_editor(pd.DataFrame(fb["criteria"]), hide_index=True)   # teacher can edit marks
    st.metric("Total", f"{table['awarded'].sum()} / {table['max'].sum()}")
    st.write(fb["overall"])
    st.info("Next step: " + fb["next_step"])
    st.warning("Review every mark before sharing with students.")
