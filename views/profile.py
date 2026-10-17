"""Profile & API keys."""
import streamlit as st

from core import auth, db, llm

u = auth.current_user()
st.title("⚙️ Profile & API Keys")

t_keys, t_profile = st.tabs(["🔑 API keys & models", "👤 My profile"])

with t_keys:
    st.markdown("Paste your free keys here to use AI features. Keys typed here are kept **only for this browser session** "
                "(never saved to the database). To keep a key permanently, see *Save keys permanently* below.")
    st.session_state.setdefault("api_keys", {})
    st.session_state.setdefault("default_models", {})
    for name, p in llm.PROVIDERS.items():
        from_secrets = bool(llm._secret(p["secret"]))
        with st.container(border=True):
            a, b = st.columns([3, 2])
            a.markdown(f"**{name}** — [get a free key]({p['get_key']})  \n<small>💳 {p['card']}</small>", unsafe_allow_html=True)
            if from_secrets:
                b.success("Loaded from app secrets")
            typed = b.text_input(f"{name} key", type="password", key=f"key_in_{name}", label_visibility="collapsed",
                                 placeholder="Paste key…" if not from_secrets else "Override for this session (optional)")
            if typed:
                st.session_state.api_keys[name] = typed.strip()
            if llm.get_key(name):
                c1, c2, c3 = st.columns([1, 1, 2])
                if c1.button("🔌 Test", key=f"test_{name}", width="stretch"):
                    res = llm.chat([{"role": "user", "content": "Reply with exactly: OK"}], provider=name,
                                   model=llm.default_model(name), max_tokens=300, temperature=0)
                    if res["error"]:
                        st.error(f"{res['error']}")
                        st.caption("If the model was not found, load the live list and choose another model.")
                    else:
                        st.success(f"Works! {llm.default_model(name)} replied in {res['latency']:.1f}s: {res['text'][:60]}")
                if c2.button("📋 Live models", key=f"lm_{name}", width="stretch"):
                    st.session_state[f"show_models_{name}"] = True
                if st.session_state.get(f"show_models_{name}"):
                    models = llm.list_models(name) or p["models"]
                    cur = llm.default_model(name)
                    sel = c3.selectbox("Default model", models, index=models.index(cur) if cur in models else 0,
                                       key=f"dm_{name}")
                    st.session_state.default_models[name] = sel
    avail = llm.available_providers()
    if avail:
        cur = llm.default_provider()
        st.session_state.default_provider = st.selectbox("Default provider for tutor & feedback", avail,
                                                         index=avail.index(cur) if cur in avail else 0)

    with st.expander("💾 Save keys permanently (recommended)"):
        st.markdown("**On your computer:** create the file `.streamlit/secrets.toml` in the project folder:")
        st.code('GROQ_API_KEY = "gsk_..."\nGEMINI_API_KEY = ""\nMISTRAL_API_KEY = ""\nOPENROUTER_API_KEY = ""\nHF_TOKEN = ""\n'
                'TEACHER_CODE = "choose-a-secret-code"', language="toml")
        st.markdown("**On Streamlit Cloud:** app → ⋮ → *Settings* → *Secrets* → paste the same lines.\n\n"
                    "⚠️ `secrets.toml` is listed in `.gitignore`, so it never goes to GitHub. Never paste keys into code or chat.")

with t_profile:
    with st.form("profile"):
        name = st.text_input("Name", u["name"])
        focus = st.text_input("My subject / focus", u.get("focus") or "",
                              placeholder="e.g. Commerce, B.Ed, UGC NET Paper 1, Physics…",
                              help="The tutor and AI-generated practice use examples from this subject. Leave blank for general.")
        goal = st.text_input("What I want to build", u.get("goal") or "")
        if st.form_submit_button("Save", type="primary"):
            db.update_user(u["username"], name=name.strip() or u["name"], focus=focus.strip(), goal=goal.strip())
            auth.refresh_user()
            st.success("Saved.")
    with st.form("pw"):
        st.markdown("**Change password**")
        old = st.text_input("Current password", type="password")
        new = st.text_input("New password (6+ characters)", type="password")
        if st.form_submit_button("Change password"):
            full = db.get_user(u["username"])
            if not auth.verify_password(old, full["pw_hash"], full["salt"]):
                st.error("Current password is wrong.")
            elif len(new) < 6:
                st.error("New password is too short.")
            else:
                h, s = auth.hash_password(new)
                db.update_user(u["username"], pw_hash=h, salt=s)
                st.success("Password changed.")
    st.caption(f"Username: {u['username']} · Role: {u['role']} · Joined {str(u.get('created_at', ''))[:10]}")
