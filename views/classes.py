"""Classes: catalogue by level (with plain descriptions), and the lesson view (Learn → Practice → Quiz → Tutor)."""
import streamlit as st

from core import auth, db, scoring, ui
from core.curriculum import LESSONS, LEVELS, LEVEL_ABOUT, LESSON_BY_ID

u = auth.current_user()
progress = db.get_progress(u["username"])


def status_icon(lid):
    p = progress.get(lid)
    if not p:
        return "⬜"
    if p["completed"]:
        return "✅"
    return "🟡"


def open_lesson(lid):
    st.session_state.open_lesson = lid
    db.log_event(u["username"], "open_lesson", lid)


lid = st.session_state.get("open_lesson")

# =============================================================================
# Catalogue
# =============================================================================
if not lid or lid not in LESSON_BY_ID:
    st.title("📚 Classes")
    with st.container(border=True):
        st.markdown("""
**What you'll find here:** 21 short lessons arranged in 4 levels, from complete beginner to building and publishing
your own AI apps. Do them in order — each lesson uses what you learned in the one before.

**Every lesson has the same 4 parts:**
1. **📖 Learn** – a plain-language explanation with examples. Just read.
2. **🛠️ Practice** – first a *guided* exercise (you can fill the blanks by choosing from a list), then one *on your own*.
   A step-by-step guide and a symbols helper are always there.
3. **✅ Quiz** – 4 quick questions. Score 60% or more to complete the lesson (you can retake it).
4. **🧑‍🏫 Tutor** – ask anything, any time. Press *"I don't know"* and it explains from the beginning, step by step.

**Status:** ✅ complete · 🟡 started · ⬜ not started · 👉 your next lesson
""")
    nxt = scoring.next_lesson(progress)
    for lv, (name, _desc) in LEVELS.items():
        ls = [l for l in LESSONS if l["level"] == lv]
        d = sum(1 for l in ls if progress.get(l["id"], {}).get("completed"))
        with st.expander(f"{name}  —  {d}/{len(ls)} complete", expanded=(nxt is not None and nxt["level"] == lv)):
            st.info(f"**In this level:** {LEVEL_ABOUT[lv]}")
            for l in ls:
                p = progress.get(l["id"], {})
                sc = scoring.lesson_score(p) if p else None
                with st.container(border=True):
                    a, c = st.columns([6, 1])
                    star = "  👉 **your next lesson**" if nxt and l["id"] == nxt["id"] else ""
                    a.markdown(f"{status_icon(l['id'])} **{l['id']} · {l['title']}**{star}")
                    a.markdown(l["about"])
                    n_code = sum(1 for e in l["practice"] if e["kind"] == "code")
                    a.caption(f"Skill: {l['skill']} · about {l['minutes']} min · "
                              + (f"{n_code} coding exercise(s)" if n_code else "no coding — reading & thinking")
                              + (f" · your score {sc:.0%}" if sc is not None else ""))
                    if c.button("Open", key=f"open_{l['id']}", width="stretch",
                                type="primary" if nxt and l["id"] == nxt["id"] else "secondary"):
                        open_lesson(l["id"])
                        st.rerun()
    st.stop()

# =============================================================================
# Lesson view
# =============================================================================
lesson = LESSON_BY_ID[lid]
idx = [l["id"] for l in LESSONS].index(lid)

top = st.columns([2, 5, 1, 1])
if top[0].button("← All classes"):
    st.session_state.open_lesson = None
    st.rerun()
if idx > 0 and top[2].button("◀ Prev", width="stretch"):
    open_lesson(LESSONS[idx - 1]["id"])
    st.rerun()
if idx < len(LESSONS) - 1 and top[3].button("Next ▶", width="stretch"):
    open_lesson(LESSONS[idx + 1]["id"])
    st.rerun()

st.title(f"{lesson['id']} · {lesson['title']}")
p = progress.get(lid, {})
st.caption(f"{LEVELS[lesson['level']][0]} · Skill: **{lesson['skill']}** · about {lesson['minutes']} min"
           + (f" · Best quiz {p['quiz_best']:.0%}" if p.get("quiz_attempts") else "")
           + (" · ✅ Complete" if p.get("completed") else ""))

with st.container(border=True):
    st.markdown(f"**📌 What this lesson is about**  \n{lesson['about']}")
    st.markdown("**🎯 By the end you will be able to:**")
    for o in lesson["objectives"]:
        st.markdown(f"- {o}")
    st.caption("How to do it: read **1 · Learn** → try **2 · Practice** → take the **3 · Quiz**. "
               "Confused at any point? Open the **🧑‍🏫 Tutor** tab and press *I don't know*.")

t_learn, t_prac, t_quiz, t_tutor = st.tabs(["📖 1 · Learn", "🛠️ 2 · Practice", "✅ 3 · Quiz", "🧑‍🏫 Tutor (ask anything)"])

with t_learn:
    st.markdown(lesson["learn"])
    st.divider()
    st.markdown("**🤔 Check yourself — can you answer these?** If not, click *Explain* and the tutor will walk you through it.")
    for i, q in enumerate(lesson["think"]):
        a, b = st.columns([5, 1])
        a.markdown(f"- *{q}*")
        if b.button("Explain", key=f"think_{lid}_{i}", width="stretch"):
            ui.seed_tutor(lid, f"Please explain this step by step for a beginner: {q}", "dont_know")
            st.toast("Open the 🧑‍🏫 Tutor tab — your explanation is ready.")

with t_prac:
    st.caption("Start with the guided exercise. Use **👣 Show step** for a step-by-step guide, **🔣 Symbols & syntax helper** "
               "to copy brackets, quotes and code patterns, and **🤷 I don't know how** for a full explanation.")
    for i, ex in enumerate(lesson["practice"]):
        label = "🤝 Guided — we do it together" if i == 0 and len(lesson["practice"]) > 1 else "🙋 On your own"
        if len(lesson["practice"]) == 1:
            label = "🙋 Your turn"
        with st.container(border=True):
            st.caption(label)
            ui.render_exercise(lesson, ex, i)

with t_quiz:
    st.caption("Score 60% or more to complete the lesson. You can retake it — your best score counts.")
    ui.render_quiz(lesson)

with t_tutor:
    ui.answer_pending(lesson["id"], lesson)
    ui.tutor_panel(lesson["id"], lesson,
                   intro=f"Hi! I'm your tutor for **{lesson['title']}**. Ask me anything about it and I'll explain "
                         "**step by step, in simple words**.\n\nNot sure what to ask? Press **🤷 I don't know – explain step by step**.")
