"""Quiz & question-bank generator — starter template.
Run: streamlit run quiz_generator.py   (needs GROQ_API_KEY in .streamlit/secrets.toml)
Ideas to extend: difficulty levels, upload syllabus, export to Google Forms, save to a database.
"""
import json

import pandas as pd
import requests
import streamlit as st
from pydantic import BaseModel, ValidationError, model_validator

st.set_page_config(page_title="Quiz Generator", page_icon="📝")

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


class MCQ(BaseModel):
    question: str
    options: list[str]
    answer: str
    explanation: str

    @model_validator(mode="after")
    def check(self):
        if len(self.options) != 4 or self.answer not in self.options:
            raise ValueError("bad question")
        return self


st.title("📝 Quiz Generator")
topic = st.text_input("Topic", "Photosynthesis")
n = st.slider("Number of questions", 3, 10, 5)
if st.button("Generate", type="primary"):
    raw = ask([
        {"role": "system", "content": "You are an expert examiner. Output only JSON."},
        {"role": "user", "content": f"Write {n} MCQs on {topic}. "
         'JSON: {"questions":[{"question":"","options":["","","",""],"answer":"<exact option>","explanation":""}]}'},
    ], json_mode=True)
    good = []
    for q in json.loads(raw)["questions"]:
        try:
            good.append(MCQ(**q).model_dump())
        except ValidationError:
            pass
    st.session_state.quiz = good

if "quiz" in st.session_state:
    score = 0
    for i, q in enumerate(st.session_state.quiz):
        pick = st.radio(f"**{i+1}. {q['question']}**", q["options"], index=None, key=f"q{i}")
        if pick:
            if pick == q["answer"]:
                score += 1
                st.success("Correct! " + q["explanation"])
            else:
                st.error(f"Answer: {q['answer']}. {q['explanation']}")
    st.metric("Score", f"{score}/{len(st.session_state.quiz)}")
    st.download_button("Download CSV", pd.DataFrame(st.session_state.quiz).to_csv(index=False), "quiz.csv")
