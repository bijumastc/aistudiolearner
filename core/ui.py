"""Reusable building blocks for pages: tutor chat, quizzes and the three kinds of exercise."""
import random

import streamlit as st

from core import db, llm, tutor
from core.curriculum import PATTERN_GROUPS_BY_SKILL, PATTERNS, SYMBOLS, blank_answers
from core.runner import run_code
from core.scoring import PASS_MARK


def user():
    return st.session_state.get("user")


def code_runner_enabled():
    try:
        return str(st.secrets.get("ALLOW_CODE_RUNNER", "true")).lower() != "false"
    except Exception:
        return True


# =============================================================================
# Tutor panel — explains step by step
# =============================================================================
def tutor_panel(key, lesson=None, persona=None, extra_context="", height=420, intro=None):
    hist_key = f"chat_{key}"
    st.session_state.setdefault(hist_key, [])
    history = st.session_state[hist_key]
    has_ai = llm.default_provider() is not None

    box = st.container(height=height)
    with box:
        if not history:
            st.chat_message("assistant", avatar="🧑‍🏫").markdown(intro or (
                "Hi! I'm your tutor. Ask me anything — I'll explain it **step by step, in simple words**.\n\n"
                "Don't know where to start? Just press **🤷 I don't know – explain step by step**."))
        for m in history:
            st.chat_message(m["role"], avatar="🧑‍🎓" if m["role"] == "user" else "🧑‍🏫").markdown(m["content"])

    def send(text, mode="explain"):
        history.append({"role": "user", "content": text})
        if has_ai:
            with st.spinner("Preparing a step-by-step explanation…"):
                ans = tutor.reply(history, user(), lesson, mode, persona, extra_context)
        else:
            ans = tutor.offline_help(lesson)
        if ans:
            history.append({"role": "assistant", "content": ans})
            db.log_event(user()["username"], "tutor", lesson["id"] if lesson else key)
        else:
            history.pop()

    with st.form(f"tutor_form_{key}", clear_on_submit=True):
        text = st.text_area("Your message", height=80, label_visibility="collapsed",
                            placeholder="Type your question, or paste your code / an error message…")
        c1, c2 = st.columns(2)
        sent = c1.form_submit_button("Send ➤", type="primary", width="stretch")
        dont = c2.form_submit_button("🤷 I don't know – explain step by step", width="stretch")
        c3, c4, c5, c6 = st.columns(4)
        simpler = c3.form_submit_button("🔍 Explain more simply", width="stretch")
        example = c4.form_submit_button("🧪 Another example", width="stretch")
        check = c5.form_submit_button("✅ Check my understanding", width="stretch")
        clear = c6.form_submit_button("🗑️ New chat", width="stretch")

    topic = f"'{lesson['title']}'" if lesson else "this"
    if sent and text.strip():
        send(text.strip())
        st.rerun()
    if dont:
        send(text.strip() or f"I don't know where to start with {topic}. Please explain it step by step from the beginning.",
             "dont_know")
        st.rerun()
    if simpler:
        send(text.strip() or "Please explain that again more simply.", "simpler")
        st.rerun()
    if example:
        send(text.strip() or "Please show me another worked example.", "example")
        st.rerun()
    if check:
        send(text.strip() or f"Please check whether I understood {topic}.", "check")
        st.rerun()
    if clear:
        st.session_state[hist_key] = []
        st.rerun()
    if not has_ai:
        st.info("No AI key yet, so the tutor shows the lesson's own step-by-step summary. "
                "Add a free Groq key in **Profile & API Keys** to ask anything in your own words.")


def seed_tutor(key, message, mode="explain"):
    """Start a tutor conversation from elsewhere (a wrong quiz answer, a code error…)."""
    st.session_state[f"chat_{key}"] = [{"role": "user", "content": message}]
    st.session_state[f"pending_{key}"] = mode


def answer_pending(key, lesson=None):
    mode = st.session_state.pop(f"pending_{key}", None)
    if mode:
        hist = st.session_state[f"chat_{key}"]
        if llm.default_provider():
            with st.spinner("Preparing a step-by-step explanation…"):
                ans = tutor.reply(hist, user(), lesson, mode)
        else:
            ans = tutor.offline_help(lesson)
        if ans:
            hist.append({"role": "assistant", "content": ans})


# =============================================================================
# Quiz
# =============================================================================
def render_quiz(lesson):
    u = user()
    qs = lesson["quiz"]
    res_key = f"quizres_{lesson['id']}"
    with st.form(f"quiz_{lesson['id']}"):
        picks = []
        for i, q in enumerate(qs):
            picks.append(st.radio(f"**{i+1}. {q['q']}**", q["options"], index=None, key=f"qz_{lesson['id']}_{i}"))
        submitted = st.form_submit_button("Check my answers", type="primary")
    if submitted:
        if any(p is None for p in picks):
            st.warning("Please answer every question.")
        else:
            correct = [q["options"].index(p) == q["answer"] for p, q in zip(picks, qs)]
            score = sum(correct) / len(qs)
            db.record_quiz(u["username"], lesson["id"], score, PASS_MARK)
            db.record_skill_attempt(u["username"], lesson["skill"], sum(correct), len(qs), "lesson-quiz")
            db.log_event(u["username"], "quiz", f"{lesson['id']} {score:.0%}")
            st.session_state[res_key] = {"correct": correct, "picks": picks, "score": score}

    res = st.session_state.get(res_key)
    if res:
        score = res["score"]
        if score >= PASS_MARK:
            st.success(f"Score: **{score:.0%}** — lesson complete! ✅")
            if score == 1:
                st.balloons()
        else:
            st.error(f"Score: **{score:.0%}** — you need {PASS_MARK:.0%} to complete. Read the explanations below and try again.")
        for i, (ok, q) in enumerate(zip(res["correct"], qs)):
            if ok:
                st.markdown(f"✅ **Q{i+1}** — {q['why']}")
            else:
                st.markdown(f"❌ **Q{i+1}** — you chose *{res['picks'][i]}*.  \n"
                            f"The correct answer is **{q['options'][q['answer']]}** — {q['why']}")
                if st.button("🧑‍🏫 Explain this to me step by step", key=f"disc_{lesson['id']}_{i}"):
                    seed_tutor(lesson["id"], f"In the quiz I was asked: \"{q['q']}\". I chose \"{res['picks'][i]}\", "
                                             f"but the answer is \"{q['options'][q['answer']]}\". I don't understand why. "
                                             "Please explain step by step.", "dont_know")
                    st.toast("Open the 🧑‍🏫 Tutor tab — your explanation is ready.")


# =============================================================================
# Exercises
# =============================================================================
def render_exercise(lesson, ex, idx):
    exid = f"{lesson['id']}-ex{idx}"
    n = len(lesson["practice"])
    badge = {"code": "🐍 Code", "build": "🛠️ Build on your computer", "reflect": "✍️ Think & write"}[ex["kind"]]
    st.markdown(f"#### {ex['title']}  \n<small>{badge}</small>", unsafe_allow_html=True)
    st.markdown(ex["prompt"])
    if ex["kind"] == "code":
        _code_exercise(lesson, ex, exid, n)
    elif ex["kind"] == "build":
        _build_exercise(lesson, ex, exid, n)
    else:
        _reflect_exercise(lesson, ex, exid, n)


def _step_guide(ex, exid, lesson, label="step"):
    """Reveal the exercise's guide one step at a time (counts as hints)."""
    hk = f"hints_{exid}"
    st.session_state.setdefault(hk, 0)
    shown = st.session_state[hk]
    steps = ex.get("hints", [])
    for i in range(shown):
        st.info(f"**Step {i+1}:** {steps[i]}")
    if shown < len(steps):
        if st.button(f"👣 Show {label} {shown+1} of {len(steps)}", key=f"hb_{exid}"):
            st.session_state[hk] += 1
            db.record_hints(user()["username"], lesson["id"], st.session_state[hk])
            st.rerun()
    return shown


def syntax_helper(skill, key):
    """Symbols + ready-made code patterns, each with a copy button — for keyboards that make symbols hard."""
    with st.expander("🔣 Symbols & syntax helper — tap the copy icon ⧉, then paste (Ctrl+V or long-press → Paste)"):
        st.markdown("**Symbols**")
        cols = st.columns(4)
        for i, (label, text, meaning) in enumerate(SYMBOLS):
            with cols[i % 4]:
                st.code(text, language=None)
                st.caption(f"{label} — {meaning}")
        groups = PATTERN_GROUPS_BY_SKILL.get(skill, ["Python"])
        tabs = st.tabs([f"🧱 {g} patterns" for g in groups])
        for tab, g in zip(tabs, groups):
            with tab:
                for title, code in PATTERNS[g]:
                    st.caption(title)
                    st.code(code, language="python")
        st.caption("💡 Indentation = 4 spaces at the start of a line inside `if`, `for` or `def`. "
                   "Copy the '4 spaces' chip if your Tab key doesn't work in the box.")


def _blank_options(answers, i):
    """Correct value + plausible distractors, in a stable random order."""
    correct = answers[i]
    pool = [a for j, a in enumerate(answers) if a != correct]
    quoted = correct.startswith('"')
    generic = (['"name"', '"A"', '"user"', '"marks"', '"count"', '"system"'] if quoted else
               ["0", "1", "x", "m", "len(marks)", "m > 40", "count + 1", "True", "print", "json.dumps", "1"])
    opts = [correct]
    for o in pool + generic:
        if o not in opts and len(opts) < 4:
            opts.append(o)
    random.Random(f"{correct}-{i}").shuffle(opts)
    return opts


def _code_exercise(lesson, ex, exid, n):
    u = user()
    answers = blank_answers(ex)
    ck = f"code_{exid}"
    st.session_state.setdefault(ck, ex["starter"].strip() + "\n")
    sol_key = f"sol_{exid}"

    modes = (["🧩 Fill the blanks (choose from a list)", "⌨️ Type the code myself"] if answers
             else ["⌨️ Type the code myself"])
    mode = st.radio("How would you like to work?", modes, horizontal=True, key=f"mode_{exid}",
                    label_visibility="collapsed" if len(modes) == 1 else "visible")

    code_to_run, picks = None, None
    if mode.startswith("🧩"):
        st.caption("Each `___` in the code is a numbered blank. Choose what goes in each one — no typing needed.")
        parts = ex["starter"].strip().split("___")
        numbered = parts[0] + "".join(f"⟦{i+1}⟧" + p for i, p in enumerate(parts[1:]))
        st.code(numbered, language="python")
        picks = []
        cols = st.columns(min(len(answers), 3))
        for i in range(len(answers)):
            with cols[i % len(cols)]:
                opts = _blank_options(answers, i) + ["✏️ type my own…"]
                choice = st.selectbox(f"Blank ⟦{i+1}⟧", opts, index=None, placeholder="choose…", key=f"bl_{exid}_{i}")
                if choice == "✏️ type my own…":
                    choice = st.text_input(f"Your text for ⟦{i+1}⟧", key=f"blt_{exid}_{i}")
                picks.append(choice or "___")
        code_to_run = parts[0] + "".join(v + p for v, p in zip(picks, parts[1:]))
        st.markdown("**Your code so far**")
        st.code(code_to_run, language="python")
    else:
        if not answers and st.button("🧱 Give me a step-by-step skeleton", key=f"skel_{exid}",
                                     help="Adds comment lines (# Step 1 …) to the code box to guide you."):
            skeleton = "\n".join(f"# Step {i+1}: {h}" for i, h in enumerate(ex.get("hints", [])))
            st.session_state[ck] = st.session_state[ck].rstrip() + "\n\n" + skeleton + "\n"
            st.rerun()
        st.text_area("Your code", key=ck, height=min(110 + 22 * st.session_state[ck].count("\n"), 460),
                     help="Lines inside if / for / def start with 4 spaces.")
        code_to_run = st.session_state[ck]
        syntax_helper(lesson["skill"], exid)

    hints_used = _step_guide(ex, exid, lesson)

    c1, c2, c3 = st.columns([2, 1, 1])
    run = c1.button("▶️ Run & check", key=f"run_{exid}", type="primary", width="stretch")
    if c2.button("🤷 I don't know how", key=f"idk_{exid}", width="stretch",
                 help="The tutor explains how to solve it, step by step."):
        seed_tutor(lesson["id"], f"I'm doing the exercise '{ex['title']}':\n{ex['prompt']}\n\nStarter code:\n```python\n"
                                 f"{ex['starter'].strip()}\n```\nI don't know how to do it. Please explain step by step, "
                                 "piece by piece, telling me exactly what to type and why.", "dont_know")
        st.toast("Open the 🧑‍🏫 Tutor tab — your step-by-step explanation is ready.")
    if c3.button("👀 Solution", key=f"sb_{exid}", width="stretch",
                 help="Viewing the solution lowers this exercise's score a little."):
        st.session_state[sol_key] = True
    if st.session_state.get(sol_key):
        st.warning("Solution shown. Read each line, then try to type it yourself from memory.")
        st.code(ex["solution"].strip(), language="python")

    if run:
        if not code_runner_enabled():
            st.error("The code runner is switched off on this server. Run the code on your own computer.")
            return
        with st.spinner("Running your code…"):
            r = run_code(code_to_run, ex["tests"])
        r["picks"] = picks
        st.session_state[f"result_{exid}"] = r
        if r["passed"]:
            score = 0.4 if st.session_state.get(sol_key) else max(0.5, 1 - 0.15 * hints_used)
            if picks is not None:
                score = min(score, 0.85)      # choosing is easier than typing — try typing next time for full marks
            db.record_exercise(u["username"], lesson["id"], exid, score, n)
            db.log_event(u["username"], "exercise_pass", exid)
        else:
            db.log_event(u["username"], "exercise_fail", exid)

    r = st.session_state.get(f"result_{exid}")
    if r:
        if r.get("picks") is not None and answers:
            marks = ["✅" if p.strip() == a else "❌" for p, a in zip(r["picks"], answers)]
            st.markdown("**Blanks:** " + "  ".join(f"⟦{i+1}⟧ {m}" for i, m in enumerate(marks)))
        if r["stdout"]:
            st.markdown("**Output**")
            st.code(r["stdout"])
        if r["passed"]:
            st.success("🎉 All tests passed! Well done.")
            if r.get("picks") is not None:
                st.caption("Next challenge: switch to **⌨️ Type the code myself** and type it from memory for full marks.")
        else:
            st.error(r["error"])
            if st.button("🧑‍🏫 Explain this error step by step", key=f"errhelp_{exid}"):
                seed_tutor(lesson["id"], f"I'm doing the exercise '{ex['title']}'. My code:\n```python\n"
                                         f"{code_to_run}\n```\nI got this error: {r['error']}\n"
                                         "Please explain step by step what it means and exactly how to fix it.", "dont_know")
                st.toast("Open the 🧑‍🏫 Tutor tab — your explanation is ready.")


def _build_exercise(lesson, ex, exid, n):
    u = user()
    st.caption("Do these steps on your own computer and tick each one when it works.")
    done = [st.checkbox(item, key=f"chk_{exid}_{i}") for i, item in enumerate(ex["checklist"])]
    _step_guide(ex, exid, lesson, "tip")
    c1, c2 = st.columns(2)
    if c1.button("💾 Save my progress", key=f"save_{exid}", width="stretch"):
        score = sum(done) / len(done)
        db.record_exercise(u["username"], lesson["id"], exid, score, n)
        db.log_event(u["username"], "build", f"{exid} {score:.0%}")
        st.success(f"Saved: {sum(done)}/{len(done)} steps done.")
    if c2.button("🤷 Walk me through it step by step", key=f"idkb_{exid}", width="stretch"):
        seed_tutor(lesson["id"], f"I need to do this on my computer: '{ex['title']}' — {ex['prompt']}\nSteps: "
                                 + "; ".join(ex["checklist"]) + "\nI'm a complete beginner. Walk me through it step by step, "
                                 "telling me exactly what to click and type (I use Windows unless I say otherwise).", "dont_know")
        st.toast("Open the 🧑‍🏫 Tutor tab — your walkthrough is ready.")
    with st.expander("🔍 Paste your code or error message for help"):
        code = st.text_area("Your code or error", key=f"rev_{exid}", height=180)
        if st.button("Explain / review it", key=f"revb_{exid}") and code.strip():
            seed_tutor(lesson["id"], f"For '{ex['title']}', here is my code or error:\n```\n{code}\n```\n"
                                     "Please explain step by step what's happening and how to fix or improve it.", "dont_know")
            st.toast("Open the 🧑‍🏫 Tutor tab for your explanation.")


def _reflect_exercise(lesson, ex, exid, n):
    u = user()
    st.markdown("**Your answer should cover:**")
    for r in ex["rubric"]:
        st.markdown(f"- {r}")
    text = st.text_area("Your answer", key=f"ref_{exid}", height=180)
    _step_guide(ex, exid, lesson, "tip")
    has_ai = llm.default_provider() is not None
    fb_key = f"fb_{exid}"
    if has_ai:
        if st.button("📝 Get feedback", key=f"fbb_{exid}", type="primary") and text.strip():
            with st.spinner("Reading your answer…"):
                fb = tutor.grade_reflection(text, ex["rubric"], ex["prompt"], u)
            if fb:
                st.session_state[fb_key] = fb
                db.record_exercise(u["username"], lesson["id"], exid, fb["score"], n)
                db.log_event(u["username"], "reflect", f"{exid} {fb['score']:.0%}")
        fb = st.session_state.get(fb_key)
        if fb:
            for i, r in enumerate(ex["rubric"]):
                st.markdown(("✅ " if i + 1 in fb["met"] else "⬜ ") + r)
            if fb.get("strength"):
                st.success("**What you did well:** " + fb["strength"])
            if fb.get("improve"):
                st.info("**To improve:** " + fb["improve"])
            if fb.get("model_answer"):
                with st.expander("📄 See a model answer to compare"):
                    st.markdown(fb["model_answer"])
    else:
        st.caption("Self-check (add an AI key for personalised feedback): tick what your answer includes.")
        ticks = [st.checkbox(r, key=f"self_{exid}_{i}") for i, r in enumerate(ex["rubric"])]
        if st.button("Save self-check", key=f"selfb_{exid}") and text.strip():
            score = sum(ticks) / len(ticks)
            db.record_exercise(u["username"], lesson["id"], exid, score, n)
            st.success(f"Saved ({score:.0%}).")


# =============================================================================
# Misc
# =============================================================================
def provider_model_picker(key, default_provider=None):
    """Provider + model selectors used in Model Lab and App Gallery."""
    avail = llm.available_providers()
    if not avail:
        st.warning("🔑 No AI key yet. Add your free Groq key in **Profile & API Keys**.")
        return None, None
    dp = default_provider if default_provider in avail else llm.default_provider()
    c1, c2 = st.columns(2)
    provider = c1.selectbox("Provider", avail, index=avail.index(dp), key=f"prov_{key}")
    live = llm.list_models(provider)
    options = live or llm.PROVIDERS[provider]["models"]
    dm = llm.default_model(provider)
    idx = options.index(dm) if dm in options else 0
    model = c2.selectbox("Model", options, index=idx, key=f"model_{key}_{provider}",
                         help="Live list from the provider" if live else "Suggested models (could not load live list)")
    return provider, model


def shuffle_options(q, seed):
    rnd = random.Random(seed)
    order = list(range(len(q["options"])))
    rnd.shuffle(order)
    return [q["options"][i] for i in order], order.index(q["answer"])
