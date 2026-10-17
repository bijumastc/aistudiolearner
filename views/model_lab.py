"""Model Lab: get to know different providers and models — playground, blind arena, leaderboard, platform guide."""
import random
from collections import defaultdict

import pandas as pd
import streamlit as st

from core import auth, db, llm, ui

u = auth.current_user()
st.title("🧪 Model Lab")
st.caption("Try different language models from different developer platforms — side by side, with the real code shown.")

t_play, t_arena, t_board, t_guide = st.tabs(["🎛️ Playground", "⚔️ Arena (blind compare)", "🏆 Class leaderboard", "🗺️ Platform guide"])

# =============================================================================
with t_play:
    provider, model = ui.provider_model_picker("play")
    if provider:
        system = st.text_area("System prompt (rules / role)", "You are a helpful university tutor. Answer clearly in under 120 words.",
                              height=70)
        prompt = st.text_area("User prompt", "Explain the difference between a population and a sample with a classroom example.",
                              height=90)
        c1, c2 = st.columns(2)
        temp = c1.slider("Temperature", 0.0, 1.5, 0.3, 0.1, help="0 = focused & repeatable, higher = more varied")
        max_t = c2.slider("Max output tokens", 100, 4000, 1200, 100,
                          help="Reasoning models (e.g. GPT-OSS) use some tokens for thinking, so leave room.")
        if st.button("▶️ Run", type="primary"):
            with st.spinner(f"Asking {model}…"):
                res = llm.chat([{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                               provider=provider, model=model, temperature=temp, max_tokens=max_t)
            db.log_event(u["username"], "model_lab", f"{provider}/{model}")
            if res["error"]:
                st.error(res["error"])
            else:
                st.markdown(res["text"] or "_(empty reply — try more max tokens)_")
                us = res["usage"]
                m1, m2, m3 = st.columns(3)
                m1.metric("Time", f"{res['latency']:.1f} s")
                m2.metric("Prompt tokens", us.get("prompt_tokens", "—"))
                m3.metric("Answer tokens", us.get("completion_tokens", "—"))
        with st.expander("🐍 See this as Python code"):
            st.code(llm.python_snippet(provider, model, system, prompt, temp), language="python")

# =============================================================================
with t_arena:
    st.markdown("Send the **same prompt** to two models. Answers are shown as **A** and **B** so brand names don't bias you. "
                "Vote, then the names are revealed.")
    st.markdown("**Model A**")
    pa, ma = ui.provider_model_picker("arena_a")
    st.markdown("**Model B**")
    pb, mb = ui.provider_model_picker("arena_b")
    if pa and pb:
        aprompt = st.text_area("Prompt for both", "Write 2 higher-order (Bloom's: Analyse) questions about climate change for B.A. students.",
                               key="arena_prompt")
        if st.button("⚔️ Run both", type="primary"):
            pair = [(pa, ma), (pb, mb)]
            random.shuffle(pair)        # hide which is which
            outs = []
            for prov, mod in pair:
                with st.spinner("Generating…"):
                    outs.append(llm.chat([{"role": "user", "content": aprompt}], provider=prov, model=mod,
                                         temperature=0.4, max_tokens=1500))
            st.session_state.arena = {"pair": pair, "outs": outs, "prompt": aprompt, "voted": None}
        ar = st.session_state.get("arena")
        if ar:
            ca, cb = st.columns(2)
            for col, label, out in zip((ca, cb), "AB", ar["outs"]):
                with col.container(border=True):
                    st.markdown(f"### {label}")
                    st.markdown(f"❌ {out['error']}" if out["error"] else (out["text"] or "_(empty reply)_"))
                    st.caption(f"{out['latency']:.1f} s")
            if not ar["voted"]:
                v1, v2, v3, v4 = st.columns(4)
                for col, choice in zip((v1, v2, v3, v4), ["A is better", "B is better", "Tie", "Both bad"]):
                    if col.button(choice, width="stretch"):
                        names = [f"{p}/{m}" for p, m in ar["pair"]]
                        winner = {"A is better": names[0], "B is better": names[1], "Tie": "tie", "Both bad": "both_bad"}[choice]
                        db.record_vote(u["username"], ar["prompt"], names[0], names[1], winner)
                        db.log_event(u["username"], "model_lab", "arena vote")
                        ar["voted"] = choice
                        st.rerun()
            else:
                st.success(f"You voted: **{ar['voted']}**. A was **{ar['pair'][0][1]}** ({ar['pair'][0][0]}), "
                           f"B was **{ar['pair'][1][1]}** ({ar['pair'][1][0]}). Surprised?")

# =============================================================================
with t_board:
    votes = db.get_votes()
    if not votes:
        st.info("No votes yet. Use the Arena — every learner's votes build this class leaderboard.")
    else:
        stats = defaultdict(lambda: {"battles": 0, "wins": 0})
        for v in votes:
            for m in (v["model_a"], v["model_b"]):
                stats[m]["battles"] += 1
            if v["winner"] not in ("tie", "both_bad"):
                stats[v["winner"]]["wins"] += 1
        df = pd.DataFrame([{"Model": m, "Battles": s["battles"], "Wins": s["wins"],
                            "Win rate": s["wins"] / s["battles"]} for m, s in stats.items()]).sort_values("Win rate", ascending=False)
        st.dataframe(df, hide_index=True, width="stretch",
                     column_config={"Win rate": st.column_config.ProgressColumn(format="%.0f%%", min_value=0, max_value=1)})
        st.caption(f"{len(votes)} votes from your class. Small samples are noisy — what would make this fairer?")

# =============================================================================
with t_guide:
    st.markdown("All five platforms speak the same **OpenAI-compatible** language: change the **base URL**, the **key** "
                "and the **model** — the code stays the same. Status shows whether *you* have a key set.")
    for name, p in llm.PROVIDERS.items():
        with st.container(border=True):
            a, b = st.columns([4, 1])
            a.markdown(f"#### {name}\n{p['about']}\n\n💳 {p['card']}  \n🔗 Get a key: {p['get_key']}  \n"
                       f"`base_url = {p['base_url']}`")
            b.markdown("✅ key set" if llm.get_key(name) else "⬜ no key")
    st.info("Tip: models are retired often (Groq retired Llama 3.3 70B in Aug 2026). The model menus in this app load the "
            "**live** list from each provider, so you always see what exists today.")
