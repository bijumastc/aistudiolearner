"""
AI Learning Studio — main entry point.
Run:  streamlit run app.py

This file only does three things:
  1. set up the page and database
  2. show the login screen if nobody is logged in
  3. build the navigation menu (pages live in the views/ folder)
"""
import streamlit as st

from core import auth, db, scoring
from core.curriculum import LESSONS, LEVELS

st.set_page_config(page_title="AI Learning Studio", page_icon="🎓", layout="wide")
db.init_db()

st.markdown("""
<style>
  .block-container {padding-top: 2rem; max-width: 1200px;}
  div[data-testid="stMetricValue"] {font-size: 1.6rem;}
</style>
""", unsafe_allow_html=True)

user = auth.current_user()

if not user:
    st.navigation([st.Page(auth.login_page, title="Log in", icon="🔑")]).run()
    st.stop()

pages = {
    "Learn": [
        st.Page("views/dashboard.py", title="My Dashboard", icon="📊", default=True),
        st.Page("views/classes.py", title="Classes", icon="📚"),
        st.Page("views/practice_gym.py", title="Practice Gym", icon="🏋️"),
        st.Page("views/tutor_page.py", title="Ask the Tutor", icon="🧑‍🏫"),
    ],
    "Explore": [
        st.Page("views/model_lab.py", title="Model Lab", icon="🧪"),
        st.Page("views/data_lab.py", title="Data Lab", icon="📈"),
        st.Page("views/app_gallery.py", title="App Gallery", icon="🧰"),
    ],
    "Account": [st.Page("views/profile.py", title="Profile & API Keys", icon="⚙️")],
}
if user["role"] == "teacher":
    pages["Account"].append(st.Page("views/teacher.py", title="Teacher View", icon="👩‍🏫"))

with st.sidebar:
    progress = db.get_progress(user["username"])
    done = sum(1 for p in progress.values() if p["completed"])
    level = scoring.current_level(progress)
    st.markdown(f"### 👋 {user['name'].split()[0]}")
    st.caption(f"{LEVELS[level][0]}" + ("  ·  👩‍🏫 Teacher" if user["role"] == "teacher" else ""))
    st.progress(done / len(LESSONS), text=f"{done}/{len(LESSONS)} lessons complete")
    if st.button("Log out", width="stretch"):
        auth.logout()
        st.rerun()

st.navigation(pages).run()
