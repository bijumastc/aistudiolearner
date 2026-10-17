"""Learner dashboard: progress, skill mastery, strengths & weaknesses, next steps."""
import altair as alt
import pandas as pd
import streamlit as st

from core import auth, db, llm, scoring
from core.curriculum import COURSE_ABOUT, LESSONS, LEVEL_ABOUT, LEVELS, LESSON_BY_ID

u = auth.current_user()
progress = db.get_progress(u["username"])
report = scoring.skill_report(u["username"])
strong, developing, weak = scoring.strengths_and_weaknesses(report)

st.title(f"📊 Welcome, {u['name'].split()[0]}!")

# ---------------- course description (always first) ----------------
with st.expander("📘 About this course — what you'll learn and how it works", expanded=not progress):
    st.markdown(COURSE_ABOUT)
    st.markdown("**The 4 levels**")
    for lv, (name, _) in LEVELS.items():
        st.markdown(f"- **{name}** — {LEVEL_ABOUT[lv]}")
    st.markdown("**This dashboard shows:** your progress, your current level, your next lesson, a *skill map* "
                "(how well you're doing in each of 10 skills), your strong and weak areas, and what to practise next.")

# ---------------- onboarding for new learners ----------------
if st.session_state.get("just_signed_up") or not progress:
    with st.container(border=True):
        st.subheader("👋 Let's set you up (30 seconds)")
        with st.form("onboard"):
            exp = st.radio("How much coding have you done?",
                           ["Never written code", "A little Python", "I've built small apps", "I've used AI APIs before"])
            focus = st.text_input("Your subject / focus (optional)", u.get("focus") or "",
                                  placeholder="e.g. Commerce, B.Ed, UGC NET Paper 1, Physics…",
                                  help="The tutor and AI practice questions will use examples from this subject.")
            goal = st.text_input("What would you like to build? (optional)", u.get("goal") or "",
                                 placeholder="e.g. a quiz generator for my students")
            if st.form_submit_button("Save and show my starting point", type="primary"):
                db.update_user(u["username"], focus=focus.strip(), goal=goal.strip())
                auth.refresh_user()
                start = {"Never written code": "L0-1", "A little Python": "L0-4",
                         "I've built small apps": "L2-1", "I've used AI APIs before": "L2-4"}[exp]
                st.session_state.start_lesson = start
                st.session_state.just_signed_up = False
                st.rerun()
    if st.session_state.get("start_lesson"):
        l = LESSON_BY_ID[st.session_state.start_lesson]
        st.success(f"Recommended start: **{l['id']} · {l['title']}**. Earlier lessons stay open for revision anytime.")

# ---------------- headline numbers ----------------
done = sum(1 for p in progress.values() if p["completed"])
quiz_scores = [p["quiz_best"] for p in progress.values() if p["quiz_attempts"]]
streak, active_days = scoring.streak(u["username"])
level = scoring.current_level(progress)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Lessons complete", f"{done}/{len(LESSONS)}")
c2.metric("Current level", f"Level {level}", help=LEVELS[level][0])
c3.metric("Average quiz score", f"{sum(quiz_scores)/len(quiz_scores):.0%}" if quiz_scores else "—")
c4.metric("Learning streak", f"{streak} day{'s' if streak != 1 else ''}", help=f"Active on {active_days} days in total")

# ---------------- continue ----------------
nxt = LESSON_BY_ID.get(st.session_state.get("start_lesson")) if not done else None
nxt = nxt or scoring.next_lesson(progress)
with st.container(border=True):
    if nxt:
        a, b = st.columns([4, 1])
        a.markdown(f"**▶️ Up next:** {nxt['id']} · {nxt['title']}  \n"
                   f"<small>{LEVELS[nxt['level']][0]} · {nxt['skill']} · ~{nxt['minutes']} min</small>",
                   unsafe_allow_html=True)
        if b.button("Continue", type="primary", width="stretch"):
            st.session_state.open_lesson = nxt["id"]
            st.switch_page("views/classes.py")
    else:
        st.markdown("🏆 **You've completed every lesson!** Build your capstone app and share it.")

# ---------------- skill mastery ----------------
st.subheader("🧠 Skill map")
st.caption("Each bar shows how well you are doing in one skill area, based on your quizzes, exercises and practice drills. "
           "Grey = not started yet. Aim to get every bar past the dashed line (75%).")
rows = [{"Skill": s, "Mastery": (r["mastery"] or 0) * 100, "Band": r["band"],
         "Lessons": f"{r['lessons_done']}/{r['lessons_total']}",
         "Drills": f"{r['drill_correct']}/{r['drill_total']}" if r["drill_total"] else "—"} for s, r in report.items()]
df = pd.DataFrame(rows)
chart = (alt.Chart(df).mark_bar(cornerRadiusEnd=4, height=18)
         .encode(x=alt.X("Mastery:Q", scale=alt.Scale(domain=[0, 100]), title="Mastery %"),
                 y=alt.Y("Skill:N", sort=None, title=None),
                 color=alt.Color("Band:N", scale=alt.Scale(domain=list(scoring.BAND_COLORS),
                                                           range=list(scoring.BAND_COLORS.values())),
                                 legend=alt.Legend(orient="bottom", title=None)),
                 tooltip=["Skill", alt.Tooltip("Mastery:Q", format=".0f"), "Band", "Lessons", "Drills"])
         .properties(height=330))
rule = alt.Chart(pd.DataFrame({"x": [75]})).mark_rule(strokeDash=[4, 4], color="#888").encode(x="x:Q")
left, right = st.columns([3, 2])
left.altair_chart(chart + rule, width="stretch")
with right:
    st.markdown("**How mastery is calculated**")
    st.caption("70% from your lesson quiz + practice scores, 30% from Practice Gym drills. "
               "Using hints or viewing solutions lowers the practice score a little — that's okay, it just "
               "tells us where to practise more. Dashed line = 'Strong' (75%).")
    st.dataframe(df[["Skill", "Band", "Lessons", "Drills"]], hide_index=True, width="stretch", height=250)

# ---------------- strengths & weaknesses ----------------
st.subheader("🎯 Your strong and weak areas")
st.caption("Strong = 75% or more · Developing = 50–74% · Needs work = below 50%. Weak areas are normal — they simply show where to practise.")
s_col, d_col, w_col = st.columns(3)
with s_col:
    st.markdown("#### 💪 Strong")
    if strong:
        for s in strong:
            st.markdown(f"- **{s}** ({report[s]['mastery']:.0%})")
    else:
        st.caption("Your strong areas will appear here as you complete lessons.")
with d_col:
    st.markdown("#### 🌱 Developing")
    for s in developing or []:
        st.markdown(f"- **{s}** ({report[s]['mastery']:.0%})")
    if not developing:
        st.caption("Nothing here yet.")
with w_col:
    st.markdown("#### 🔧 Needs work")
    for s in weak or []:
        st.markdown(f"- **{s}** ({report[s]['mastery']:.0%})")
    if not weak:
        st.caption("No weak areas detected. 🎉")

recs = scoring.recommendations(u["username"], report, progress)
if recs:
    st.markdown("#### 📌 What to do next")
    for i, r in enumerate(recs[:4]):
        with st.container(border=True):
            a, b, c = st.columns([4, 1, 1])
            a.markdown(f"**{r['skill']}** ({r['band']}): revisit *{r['lesson']['title']}* — {r['why']}.")
            if b.button("Revisit", key=f"rv_{i}", width="stretch"):
                st.session_state.open_lesson = r["lesson"]["id"]
                st.switch_page("views/classes.py")
            if c.button("Drill", key=f"dr_{i}", width="stretch"):
                st.session_state.gym_skills = [r["skill"]]
                st.switch_page("views/practice_gym.py")

# ---------------- AI study plan ----------------
with st.expander("🗓️ Get a personalised one-week study plan (AI)"):
    hours = st.slider("Hours you can study per week", 1, 15, 4)
    if st.button("Create my plan", type="primary"):
        summary = "\n".join(f"- {s}: {r['band']} ({(r['mastery'] or 0):.0%}), lessons {r['lessons_done']}/{r['lessons_total']}"
                            for s, r in report.items())
        todo = [f"{l['id']} {l['title']} ({l['skill']}, {l['minutes']} min)" for l in LESSONS
                if not progress.get(l["id"], {}).get("completed")][:8]
        plan = llm.ask([
            {"role": "system", "content": "You are a supportive learning coach. Be concrete, realistic and encouraging."},
            {"role": "user", "content": f"Learner focus: {u.get('focus') or 'general higher education'}. Goal: {u.get('goal') or 'learn to build AI apps'}.\n"
                                        f"Skill report:\n{summary}\nNext lessons available:\n" + "\n".join(todo) +
                                        f"\nMake a 7-day plan for {hours} hours total. Prioritise weak skills but keep momentum. "
                                        "Use a markdown table (Day | Activity | Time | Why), then 2 tips."},
        ], temperature=0.5)
        if plan:
            st.markdown(plan)
            db.log_event(u["username"], "study_plan")

# ---------------- level progress & activity ----------------
st.subheader("🪜 Progress by level")
st.caption("Lessons completed in each level. A level counts as done when you have completed 60% of its lessons.")
cols = st.columns(len(LEVELS))
for col, (lv, (name, desc)) in zip(cols, LEVELS.items()):
    ls = [l for l in LESSONS if l["level"] == lv]
    d = sum(1 for l in ls if progress.get(l["id"], {}).get("completed"))
    col.markdown(f"**{name}**")
    col.progress(d / len(ls), text=f"{d}/{len(ls)}")

events = db.get_events(u["username"], limit=8)
if events:
    with st.expander("🕑 Recent activity"):
        icons = {"login": "🔑", "quiz": "✅", "exercise_pass": "🐍", "exercise_fail": "🔁", "tutor": "🦉",
                 "build": "🛠️", "reflect": "✍️", "drill": "🎯", "study_plan": "🗓️", "model_lab": "🧪", "app": "🧰"}
        for e in events:
            st.markdown(f"{icons.get(e['kind'], '•')} `{e['ts'][:16].replace('T', ' ')}` {e['kind'].replace('_', ' ')} {e['detail']}")
