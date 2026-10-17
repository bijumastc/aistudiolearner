"""Practice Gym: targeted drills on weak skills, code challenges, AI-generated questions, explain-back."""
import random

import streamlit as st
from pydantic import BaseModel, ValidationError, model_validator

from core import auth, db, llm, scoring, tutor, ui
from core.curriculum import LESSON_BY_ID, LESSONS, SKILLS, code_exercises, quiz_bank

u = auth.current_user()
report = scoring.skill_report(u["username"])
_, developing, weak = scoring.strengths_and_weaknesses(report)

st.title("🏋️ Practice Gym")
st.caption("Short, focused practice. Everything here feeds your skill map on the dashboard.")

tab_drill, tab_code, tab_ai, tab_explain = st.tabs(
    ["🎯 Smart drill", "🐍 Code challenges", "🤖 Fresh AI questions", "🗣️ Explain it back"])

# =============================================================================
with tab_drill:
    st.markdown("Mixed questions from the lessons, **weighted towards your weaker skills**.")
    default = st.session_state.pop("gym_skills", None) or (weak + developing)[:3] or SKILLS[:3]
    skills = st.multiselect("Skills to drill", SKILLS, default=[s for s in default if s in SKILLS], key="drill_sk")
    n = st.slider("Number of questions", 3, 10, 5, key="drill_n")
    if st.button("🎲 New drill", type="primary") and skills:
        bank = quiz_bank(skills)
        weights = [3 if q["skill"] in weak else 2 if q["skill"] in developing else 1 for q in bank]
        chosen, pool, w = [], list(bank), list(weights)
        while pool and len(chosen) < n:
            i = random.choices(range(len(pool)), weights=w)[0]
            chosen.append(pool.pop(i))
            w.pop(i)
        st.session_state.drill = {"qs": chosen, "seed": random.randint(0, 10**6), "result": None}

    drill = st.session_state.get("drill")
    if drill:
        with st.form("drill_form"):
            picks = []
            for i, q in enumerate(drill["qs"]):
                opts, _ = ui.shuffle_options(q, drill["seed"] + i)
                picks.append(st.radio(f"**{i+1}. {q['q']}**  \n<small>{q['skill']}</small>", opts, index=None,
                                      key=f"dq_{drill['seed']}_{i}"))
            go = st.form_submit_button("Check")
        if go:
            if None in picks:
                st.warning("Answer every question first.")
            else:
                per_skill = {}
                result = []
                for i, (q, pck) in enumerate(zip(drill["qs"], picks)):
                    ok = pck == q["options"][q["answer"]]
                    result.append(ok)
                    c, t = per_skill.get(q["skill"], (0, 0))
                    per_skill[q["skill"]] = (c + ok, t + 1)
                for sk, (c, t) in per_skill.items():
                    db.record_skill_attempt(u["username"], sk, c, t, "drill")
                db.log_event(u["username"], "drill", f"{sum(result)}/{len(result)}")
                drill["result"] = result
        if drill.get("result"):
            res = drill["result"]
            st.metric("Score", f"{sum(res)}/{len(res)}")
            for i, (ok, q) in enumerate(zip(res, drill["qs"])):
                if ok:
                    st.markdown(f"✅ **Q{i+1}** {q['why']}")
                else:
                    st.markdown(f"❌ **Q{i+1}** Answer: **{q['options'][q['answer']]}** — {q['why']}  "
                                f"<small>(from lesson {q['lesson']})</small>", unsafe_allow_html=True)

# =============================================================================
with tab_code:
    st.markdown("Every coding exercise from the course, in one place. Hints are there when you need them.")
    sk = st.selectbox("Filter by skill", ["All"] + sorted({e["skill"] for e in code_exercises()}), key="code_sk")
    exs = code_exercises(None if sk == "All" else [sk])
    results = db.get_exercise_results(u["username"])
    labels = [f"{'✅' if results.get(e['exid'], 0) >= 0.5 else '⬜'} {e['lesson']} · {e['title']}" for e in exs]
    choice = st.selectbox("Choose a challenge", range(len(exs)), format_func=lambda i: labels[i], key="code_pick")
    ex = exs[choice]
    lesson = LESSON_BY_ID[ex["lesson"]]
    with st.container(border=True):
        st.caption(f"From {lesson['id']} · {lesson['title']}")
        ui.render_exercise(lesson, ex, int(ex["exid"].split("ex")[-1]))
    with st.expander("🧑‍🏫 Stuck? Ask the tutor about this challenge"):
        ui.answer_pending(lesson["id"], lesson)
        ui.tutor_panel(lesson["id"], lesson, height=300)


# =============================================================================
class GenMCQ(BaseModel):
    question: str
    options: list[str]
    answer: str
    explanation: str

    @model_validator(mode="after")
    def check(self):
        if len(self.options) != 4:
            raise ValueError("need 4 options")
        if self.answer not in self.options:
            raise ValueError("answer must be one of the options")
        return self


with tab_ai:
    st.markdown("Unlimited new questions written by an AI model for **your** subject focus — "
                "also a live example of JSON mode + Pydantic validation (Lesson L2-5).")
    c1, c2, c3 = st.columns(3)
    skill = c1.selectbox("Skill", SKILLS, index=SKILLS.index(weak[0]) if weak else 0, key="ai_sk")
    bloom = c2.selectbox("Bloom's level", ["Remember", "Understand", "Apply", "Analyse", "Evaluate"], index=2)
    n_q = c3.slider("Questions", 2, 6, 3, key="ai_n")
    if st.button("✨ Generate", type="primary"):
        notes = " ".join(l["title"] + ": " + "; ".join(l["objectives"]) for l in LESSONS if l["skill"] == skill)
        raw = llm.ask([
            {"role": "system", "content": "You write accurate multiple-choice questions for a beginner-friendly course. Output only JSON."},
            {"role": "user", "content": f"Skill: {skill}. Course content: {notes}\nLearner's subject focus: {u.get('focus') or 'general higher education'} "
                                        f"(use it for examples where natural).\nWrite {n_q} MCQs at Bloom's level '{bloom}'. "
                                        'JSON: {"questions": [{"question": "", "options": ["", "", "", ""], "answer": "<exact text of correct option>", "explanation": ""}]}'},
        ], temperature=0.4, json_mode=True, max_tokens=2500)
        if raw:
            try:
                data = llm.extract_json(raw)
                qs, rejected = [], 0
                for q in data.get("questions", []):
                    try:
                        qs.append(GenMCQ(**q).model_dump())
                    except ValidationError:
                        rejected += 1
                st.session_state.ai_quiz = {"qs": qs, "skill": skill, "done": False}
                if rejected:
                    st.info(f"Pydantic rejected {rejected} badly-formed question(s) — that's validation doing its job.")
            except Exception as e:
                st.error(f"Couldn't read the model's JSON: {e}")
    aq = st.session_state.get("ai_quiz")
    if aq and aq["qs"]:
        with st.form("aiq"):
            picks = [st.radio(f"**{i+1}. {q['question']}**", q["options"], index=None, key=f"aiq_{i}_{hash(q['question'])}")
                     for i, q in enumerate(aq["qs"])]
            go = st.form_submit_button("Check")
        if go and None not in picks:
            right = [p == q["answer"] for p, q in zip(picks, aq["qs"])]
            if not aq["done"]:
                db.record_skill_attempt(u["username"], aq["skill"], sum(right), len(right), "ai-drill")
                db.log_event(u["username"], "drill", f"AI {aq['skill']} {sum(right)}/{len(right)}")
                aq["done"] = True
            st.metric("Score", f"{sum(right)}/{len(right)}")
            for ok, q in zip(right, aq["qs"]):
                (st.success if ok else st.error)(f"{'✅' if ok else '❌'} {q['answer']} — {q['explanation']}")
            st.caption("⚠️ AI-written questions can contain mistakes. If one looks wrong, discuss it with the tutor!")

# =============================================================================
with tab_explain:
    st.markdown("**The Feynman technique:** if you can explain it simply, you understand it. "
                "Pick a lesson, explain its main idea as if to a first-year student, and get feedback with a model answer.")
    lid = st.selectbox("Lesson", [l["id"] for l in LESSONS], format_func=lambda i: f"{i} · {LESSON_BY_ID[i]['title']}",
                       key="fe_lesson")
    lesson = LESSON_BY_ID[lid]
    text = st.text_area("Your explanation", height=180, key=f"fe_text_{lid}")
    if st.button("Get feedback", type="primary", key="fe_btn") and text.strip():
        fb = tutor.grade_reflection(text, lesson["objectives"],
                                    f"Explain the main ideas of '{lesson['title']}' simply.", u)
        if fb:
            db.record_skill_attempt(u["username"], lesson["skill"], len(fb["met"]), len(lesson["objectives"]), "explain")
            db.log_event(u["username"], "drill", f"explain {lid}")
            for i, o in enumerate(lesson["objectives"]):
                st.markdown(("✅ " if i + 1 in fb["met"] else "⬜ ") + o)
            if fb.get("strength"):
                st.success("**Strength:** " + fb["strength"])
            if fb.get("improve"):
                st.info("**Improve:** " + fb["improve"])
            if fb.get("model_answer"):
                with st.expander("📄 See a model explanation to compare"):
                    st.markdown(fb["model_answer"])
