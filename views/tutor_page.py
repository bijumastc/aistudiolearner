"""Ask the Tutor: a step-by-step tutor for any topic or lesson, or a custom AI study-twin persona."""
import streamlit as st

from core import auth, ui
from core.curriculum import LESSON_BY_ID, LESSONS

u = auth.current_user()
st.title("🧑‍🏫 Ask the Tutor")
st.caption("Ask anything about coding, AI or the lessons. The tutor explains **step by step, in simple words**. "
           "Say *I don't know* (or press the button) and it starts from the very beginning.")

mode = st.radio("Who would you like to talk to?",
                ["🧑‍🏫 Course tutor (any topic)", "📚 Tutor for a specific lesson", "🤖 My custom AI study twin"],
                horizontal=True)

if mode.startswith("🧑‍🏫"):
    ui.tutor_panel("general")

elif mode.startswith("📚"):
    lid = st.selectbox("Lesson", [l["id"] for l in LESSONS], format_func=lambda i: f"{i} · {LESSON_BY_ID[i]['title']}")
    ui.answer_pending(lid, LESSON_BY_ID[lid])
    ui.tutor_panel(lid, LESSON_BY_ID[lid])

else:
    st.markdown("Design a companion persona (this is Lesson **L3-2** in action). The persona becomes the **system prompt**.")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Twin's name", "Mitra")
        style = c2.selectbox("Personality", ["Warm & encouraging", "Calm & precise", "Strict exam coach",
                                             "Curious fellow researcher", "Viva examiner (asks probing questions)"])
        group = c3.text_input("For which students?", u.get("focus") or "undergraduate students")
        mood = st.select_slider("How are you feeling today?", ["😞 low", "😐 okay", "🙂 good", "😄 great"], "🙂 good")
        extra = st.text_area("Extra rules (optional)", "Ask one question at a time. Keep replies short. "
                             "Track what I've said I studied and remind me of it.", height=70)
    persona = (f"You are {name}, an AI study companion for {group}. Personality: {style}. "
               f"The learner says their mood today is '{mood}'; adapt your tone. {extra} "
               "Never do assignments for the learner; help them think. If they seem distressed, respond with "
               "kindness and suggest talking to a trusted person or the college counsellor.")
    with st.expander("See the system prompt being sent"):
        st.code(persona, language="text")
    ui.tutor_panel(f"twin_{name}", persona=persona)
