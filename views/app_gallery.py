"""App Gallery: ready-to-use higher-education apps + downloadable starter code to build your own."""
import os

import pandas as pd
import streamlit as st
from pydantic import BaseModel, ValidationError, model_validator

from core import auth, db, llm, ui
from core.datasets import student_performance

u = auth.current_user()
FOCUS = u.get("focus") or "general higher education"
TEMPLATES = os.path.join(os.path.dirname(__file__), "..", "templates")

st.title("🧰 App Gallery")
st.caption("Useful tools for teaching and research — use them now, then download the starter code and build your own version.")

APPS = {
    "📝 Quiz & question-bank generator": "quiz_generator.py",
    "🧾 Rubric feedback assistant": "rubric_feedback.py",
    "🗂️ Lesson plan builder": "lesson_planner.py",
    "🔬 Research question refiner": None,
    "🃏 Flashcards from notes": None,
    "📊 Marks analyser & early warning (no AI)": "marks_analyzer.py",
    "📄 PDF study assistant (RAG)": "pdf_assistant.py",
}
app = st.selectbox("Choose an app", list(APPS))


def template_download(fname):
    if fname:
        with open(os.path.join(TEMPLATES, fname), encoding="utf-8") as f:
            code = f.read()
        c1, c2 = st.columns([1, 3])
        c1.download_button("📥 Starter code", code, fname, "text/x-python", width="stretch")
        with c2.expander("Peek at the code"):
            st.code(code, language="python")
    else:
        st.caption("🏗️ No template for this one — building it is a great capstone challenge (lesson L3-6)!")


def pick(key):
    p, m = ui.provider_model_picker(key)
    return p, m


st.divider()

# =============================================================================
if app.startswith("📝"):
    st.subheader(app)
    st.markdown("Generates MCQs as **validated JSON**, lets you try them, and exports a CSV for Google Forms / Moodle / Excel.")

    class Q(BaseModel):
        question: str
        options: list[str]
        answer: str
        explanation: str
        bloom: str = ""

        @model_validator(mode="after")
        def ok(self):
            if len(self.options) != 4 or self.answer not in self.options:
                raise ValueError("bad question")
            return self

    p, m = pick("g_quiz")
    c1, c2, c3 = st.columns(3)
    topic = c1.text_input("Topic", "Sampling techniques in research")
    level = c2.selectbox("Students", ["UG first year", "UG final year", "PG", "M.Phil/PhD", "Competitive exam (e.g. UGC NET)"])
    n = c3.slider("Questions", 3, 15, 5)
    blooms = st.multiselect("Bloom's levels", ["Remember", "Understand", "Apply", "Analyse", "Evaluate", "Create"],
                            ["Understand", "Apply", "Analyse"])
    if st.button("Generate", type="primary", disabled=not p):
        raw = llm.ask([{"role": "system", "content": "You are an expert examiner. Output only JSON. Questions must be factually correct and unambiguous."},
                       {"role": "user", "content": f"Write {n} MCQs on '{topic}' for {level} students, spread across Bloom's levels {blooms}. "
                                                   'JSON: {"questions":[{"question":"","options":["","","",""],"answer":"<exact option text>","explanation":"","bloom":""}]}'}],
                      provider=p, model=m, temperature=0.3, json_mode=True, max_tokens=4000)
        if raw:
            try:
                good, bad = [], 0
                for q in llm.extract_json(raw).get("questions", []):
                    try:
                        good.append(Q(**q).model_dump())
                    except ValidationError:
                        bad += 1
                st.session_state.g_quiz = good
                db.log_event(u["username"], "app", "quiz generator")
                if bad:
                    st.info(f"{bad} malformed question(s) were filtered out by validation.")
            except Exception as e:
                st.error(f"Couldn't parse JSON: {e}")
    qs = st.session_state.get("g_quiz")
    if qs:
        for i, q in enumerate(qs):
            with st.expander(f"Q{i+1} [{q['bloom']}] {q['question']}"):
                for o in q["options"]:
                    st.markdown(("✅ " if o == q["answer"] else "▫️ ") + o)
                st.caption(q["explanation"])
        df = pd.DataFrame([{"Question": q["question"], "Option A": q["options"][0], "Option B": q["options"][1],
                            "Option C": q["options"][2], "Option D": q["options"][3], "Answer": q["answer"],
                            "Bloom": q["bloom"], "Explanation": q["explanation"]} for q in qs])
        st.download_button("⬇️ Download CSV", df.to_csv(index=False), "question_bank.csv", "text/csv")
        st.warning("Always review AI-generated questions before using them with students.")
    template_download(APPS[app])

# =============================================================================
elif app.startswith("🧾"):
    st.subheader(app)
    st.markdown("Paste a rubric and a (anonymised) student answer → criterion-by-criterion feedback you can **edit before sharing**.")
    p, m = pick("g_rub")
    question = st.text_input("Question / task", "Explain the causes of the 1929 Great Depression. (10 marks)")
    rubric = st.text_area("Rubric (one criterion per line, with marks)",
                          "Identifies at least 3 causes (4)\nExplains how causes are linked (3)\nUses evidence/examples (2)\nClear structure (1)", height=110)
    answer = st.text_area("Student answer (remove names!)", height=160,
                          value="The depression happened because the stock market crashed in 1929. Banks failed and people lost money. "
                                "Also there was overproduction in farms. Many people lost jobs.")
    tone = st.select_slider("Feedback tone", ["Very gentle", "Encouraging", "Direct"], "Encouraging")
    if st.button("Get feedback", type="primary", disabled=not p):
        raw = llm.ask([{"role": "system", "content": "You are a fair, experienced examiner giving formative feedback. Output only JSON."},
                       {"role": "user", "content": f"Question: {question}\nRubric:\n{rubric}\nStudent answer:\n{answer}\nTone: {tone}.\n"
                                                   'JSON: {"criteria":[{"criterion":"","max":0,"awarded":0,"comment":""}],'
                                                   '"overall":"","next_step":"","feedforward_question":""}'}],
                      provider=p, model=m, temperature=0.1, json_mode=True, max_tokens=2500)
        if raw:
            try:
                fb = llm.extract_json(raw)
                st.session_state.g_rub = fb
                db.log_event(u["username"], "app", "rubric feedback")
            except Exception as e:
                st.error(str(e))
    fb = st.session_state.get("g_rub")
    if fb:
        df = pd.DataFrame(fb.get("criteria", []))
        edited = st.data_editor(df, width="stretch", hide_index=True, key="rub_edit")
        try:
            st.metric("Total", f"{pd.to_numeric(edited['awarded']).sum():g} / {pd.to_numeric(edited['max']).sum():g}")
        except Exception:
            pass
        st.text_area("Overall comment (editable)", fb.get("overall", ""), key="rub_overall")
        st.markdown(f"**Next step:** {fb.get('next_step', '')}  \n**Question to think about:** *{fb.get('feedforward_question', '')}*")
        st.warning("Human in the loop: check every mark. AI can be inconsistent or biased.")
    template_download(APPS[app])

# =============================================================================
elif app.startswith("🗂️"):
    st.subheader(app)
    p, m = pick("g_lp")
    c1, c2 = st.columns(2)
    topic = c1.text_input("Topic", "Introduction to hypothesis testing")
    course = c2.text_input("Course / class", f"{FOCUS} — UG")
    c3, c4, c5 = st.columns(3)
    mins = c3.selectbox("Duration", [45, 60, 90, 120], 1)
    pedagogy = c4.selectbox("Approach", ["Active learning", "Flipped classroom", "Case-based", "Project-based", "Lecture + discussion"])
    size = c5.number_input("Class size", 5, 300, 60)
    extras = st.multiselect("Include", ["Learning outcomes (Bloom's)", "Timed activities", "Formative check", "Differentiation for slow/advanced learners",
                                        "Indian / local examples", "Homework", "NEP 2020 alignment note"],
                            ["Learning outcomes (Bloom's)", "Timed activities", "Formative check", "Indian / local examples"])
    if st.button("Build plan", type="primary", disabled=not p):
        plan = llm.ask([{"role": "system", "content": "You are an experienced teacher educator. Produce practical, realistic plans in markdown."},
                        {"role": "user", "content": f"Lesson plan: '{topic}' for {course}, {mins} minutes, {size} students, approach: {pedagogy}. "
                                                    f"Include: {', '.join(extras)}. Use a timed table for activities."}],
                       provider=p, model=m, temperature=0.5, max_tokens=3000)
        if plan:
            st.session_state.g_lp = plan
            db.log_event(u["username"], "app", "lesson plan")
    if st.session_state.get("g_lp"):
        st.markdown(st.session_state.g_lp)
        st.download_button("⬇️ Download (Markdown)", st.session_state.g_lp, "lesson_plan.md")
    template_download(APPS[app])

# =============================================================================
elif app.startswith("🔬"):
    st.subheader(app)
    st.markdown("A research mentor that helps you sharpen a research question using the **FINER** criteria "
                "(Feasible, Interesting, Novel, Ethical, Relevant) — it asks, you think.")
    rq = st.text_input("Your draft research question / topic", "Impact of mobile phones on students")
    persona = ("You are a supportive research supervisor. Help the learner refine their research question using FINER "
               "criteria and, where relevant, variables, population, setting and method. Explain each criterion simply, "
               f"point out what is unclear, and suggest 2-3 improved versions. Field: {FOCUS}. Their draft: '{rq}'.")
    ui.tutor_panel(f"rq_{hash(rq) % 10**6}", persona=persona, height=360)
    template_download(APPS[app])

# =============================================================================
elif app.startswith("🃏"):
    st.subheader(app)
    p, m = pick("g_fc")
    notes = st.text_area("Paste your notes", height=180,
                         value="Validity refers to whether a test measures what it claims to measure. Reliability is the consistency "
                               "of a measure across time or raters. Content validity checks coverage of the syllabus. Test-retest reliability "
                               "correlates scores from two administrations.")
    n = st.slider("Cards", 3, 15, 6)
    if st.button("Make flashcards", type="primary", disabled=not p):
        raw = llm.ask([{"role": "system", "content": "Create study flashcards strictly from the notes. Output only JSON."},
                       {"role": "user", "content": f"Notes:\n{notes}\n\nMake {n} cards. JSON: {{\"cards\":[{{\"front\":\"\",\"back\":\"\"}}]}}"}],
                      provider=p, model=m, temperature=0.2, json_mode=True, max_tokens=2000)
        if raw:
            try:
                st.session_state.g_fc = llm.extract_json(raw).get("cards", [])
                st.session_state.fc_i, st.session_state.fc_flip = 0, False
                db.log_event(u["username"], "app", "flashcards")
            except Exception as e:
                st.error(str(e))
    cards = st.session_state.get("g_fc")
    if cards:
        i = st.session_state.fc_i % len(cards)
        c = cards[i]
        with st.container(border=True, height=180):
            st.markdown(f"<div style='text-align:center;font-size:1.3rem;padding-top:40px'>"
                        f"{c['back'] if st.session_state.fc_flip else c['front']}</div>", unsafe_allow_html=True)
        b1, b2, b3 = st.columns(3)
        if b1.button("◀ Prev", width="stretch"):
            st.session_state.fc_i -= 1; st.session_state.fc_flip = False; st.rerun()
        if b2.button("🔄 Flip", width="stretch", type="primary"):
            st.session_state.fc_flip = not st.session_state.fc_flip; st.rerun()
        if b3.button("Next ▶", width="stretch"):
            st.session_state.fc_i += 1; st.session_state.fc_flip = False; st.rerun()
        st.caption(f"Card {i+1} of {len(cards)}")
        st.download_button("⬇️ Export (CSV for Anki/Quizlet)", pd.DataFrame(cards).to_csv(index=False), "flashcards.csv")
    template_download(APPS[app])

# =============================================================================
elif app.startswith("📊"):
    st.subheader(app)
    st.markdown("Upload a marks sheet (or use the sample) to see class statistics and **students who may need support**. "
                "No AI needed — just pandas.")
    up = st.file_uploader("CSV with columns: roll_no, attendance_pct, internal, external (names can differ)", type=["csv", "xlsx"])
    if up:
        df = pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
    else:
        df = student_performance()[["roll_no", "dept", "attendance_pct", "internal_50", "external_100"]]
        st.caption("Using the built-in sample (synthetic).")
    cols = df.columns.tolist()
    c1, c2, c3, c4 = st.columns(4)
    idc = c1.selectbox("ID column", cols, 0)
    att = c2.selectbox("Attendance %", cols, min(2, len(cols) - 1))
    ints = c3.selectbox("Internal marks", cols, min(3, len(cols) - 1))
    ext = c4.selectbox("External marks", cols, min(4, len(cols) - 1))
    t1, t2, t3 = st.columns(3)
    att_cut = t1.number_input("Attendance threshold %", 0, 100, 75)
    int_max = t2.number_input("Internal max", 1, 200, 50)
    pass_pct = t3.number_input("Pass % (internal)", 0, 100, 40)
    d = df.copy()
    for c in (att, ints, ext):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["internal_pct"] = (d[ints] / int_max * 100).round(1)
    d["flags"] = ""
    d.loc[d[att] < att_cut, "flags"] += "Low attendance; "
    d.loc[d["internal_pct"] < pass_pct, "flags"] += "Low internal; "
    d.loc[d[ext].isna(), "flags"] += "Absent/missing external; "
    risk = d[d["flags"] != ""]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Students", len(d))
    m2.metric("Avg attendance", f"{d[att].mean():.1f}%")
    m3.metric("Avg internal", f"{d['internal_pct'].mean():.1f}%")
    m4.metric("Flagged", len(risk))
    st.bar_chart(pd.cut(d["internal_pct"], [0, 40, 50, 60, 75, 101], right=False,
                        labels=["<40", "40–49", "50–59", "60–74", "75+"]).value_counts().sort_index())
    st.markdown("**Students who may need support**")
    st.dataframe(risk[[idc, att, "internal_pct", ext, "flags"]], hide_index=True, width="stretch")
    st.download_button("⬇️ Download flagged list", risk.to_csv(index=False), "early_warning.csv")
    st.caption("Use flags to *offer support*, not to label students. Correlation of attendance with marks: "
               f"**{d[att].corr(d['internal_pct']):.2f}**")
    template_download(APPS[app])

# =============================================================================
elif app.startswith("📄"):
    st.subheader(app)
    st.markdown("Upload notes, a syllabus or a past paper → ask questions answered **only from the document**, with the "
                "retrieved passages shown (lesson L3-1).")
    p, m = pick("g_pdf")
    up = st.file_uploader("PDF", type="pdf")
    if up:
        from pypdf import PdfReader
        key = f"pdf_{up.name}_{up.size}"
        if st.session_state.get("pdf_key") != key:
            reader = PdfReader(up)
            pages = [(i + 1, pg.extract_text() or "") for i, pg in enumerate(reader.pages)]
            chunks = []
            for pno, text in pages:
                words = text.split()
                for j in range(0, len(words), 180):
                    chunks.append({"page": pno, "text": " ".join(words[j:j + 200])})
            st.session_state.pdf_key, st.session_state.pdf_chunks = key, chunks
        chunks = st.session_state.pdf_chunks
        st.success(f"{len(chunks)} chunks from {up.name}" if chunks else "No text found — is it a scanned PDF?")
        q = st.text_input("Your question")
        k = st.slider("Passages to retrieve", 2, 8, 4)
        if st.button("Ask", type="primary", disabled=not (p and q and chunks)):
            words = {w.lower().strip("?.,:;") for w in q.split() if len(w) > 3}
            ranked = sorted(chunks, key=lambda c: sum(c["text"].lower().count(w) for w in words), reverse=True)[:k]
            ctx = "\n\n".join(f"[p.{c['page']}] {c['text']}" for c in ranked)
            ans = llm.ask([{"role": "system", "content": "Answer ONLY from the context. Cite page numbers like (p.3). "
                                                         "If the answer isn't in the context, say 'Not found in the document.'"},
                           {"role": "user", "content": f"Context:\n{ctx}\n\nQuestion: {q}"}],
                          provider=p, model=m, temperature=0.1, max_tokens=1500)
            if ans:
                st.markdown(ans)
                db.log_event(u["username"], "app", "pdf assistant")
                with st.expander("Retrieved passages"):
                    st.text(ctx)
    template_download(APPS[app])
