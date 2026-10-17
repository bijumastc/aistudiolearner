"""Lesson plan builder — starter template.
Run: streamlit run lesson_planner.py
Ideas: save plans to a database, generate matching slides/quiz, add your institution's template.
"""
import requests
import streamlit as st

st.set_page_config(page_title="Lesson Planner", page_icon="🗂️")

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

st.title("🗂️ Lesson Plan Builder")
topic = st.text_input("Topic", "Supply and demand")
minutes = st.selectbox("Duration (minutes)", [45, 60, 90])
approach = st.selectbox("Approach", ["Active learning", "Flipped classroom", "Case-based"])

if st.button("Build plan", type="primary"):
    plan = ask([
        {"role": "system", "content": "You are an experienced teacher educator. Write practical markdown plans."},
        {"role": "user", "content": f"Lesson plan for '{topic}', {minutes} minutes, approach: {approach}. "
         "Include learning outcomes (Bloom's), a timed activity table, a formative check and homework."},
    ], temperature=0.5)
    st.session_state.plan = plan

if "plan" in st.session_state:
    st.markdown(st.session_state.plan)
    st.download_button("Download", st.session_state.plan, "lesson_plan.md")
