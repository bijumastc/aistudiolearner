"""
Login & sign-up.

Passwords are never stored. We store a salted PBKDF2 hash (a one-way fingerprint).
Teachers sign up with the TEACHER_CODE from Streamlit secrets.
"""
import hashlib
import hmac
import re
import secrets as pysecrets

import streamlit as st

from core import db


def hash_password(password, salt=None):
    salt = salt or pysecrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
    return digest, salt


def verify_password(password, pw_hash, salt):
    return hmac.compare_digest(hash_password(password, salt)[0], pw_hash)


def secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def current_user():
    return st.session_state.get("user")


def login(username, password):
    user = db.get_user(username.strip().lower())
    if user and verify_password(password, user["pw_hash"], user["salt"]):
        st.session_state.user = user
        db.log_event(user["username"], "login")
        return True
    return False


def signup(username, name, password, teacher_code=""):
    username = username.strip().lower()
    if not re.fullmatch(r"[a-z0-9_.]{3,30}", username):
        return "Username: 3–30 characters, only letters, numbers, _ or ."
    if len(password) < 6:
        return "Password must be at least 6 characters."
    if not name.strip():
        return "Please enter your name."
    if db.get_user(username):
        return "That username is taken."
    role = "student"
    if teacher_code:
        real = secret("TEACHER_CODE", "")
        if not real or teacher_code != real:
            return "Teacher code is not correct (leave it blank to join as a student)."
        role = "teacher"
    pw_hash, salt = hash_password(password)
    db.create_user(username, name.strip(), pw_hash, salt, role)
    return None


def refresh_user():
    u = current_user()
    if u:
        st.session_state.user = db.get_user(u["username"])


def logout():
    for k in list(st.session_state.keys()):
        if k != "api_keys":
            del st.session_state[k]


def login_page():
    left, mid, right = st.columns([1, 2, 1])
    with mid:
        st.markdown("<h1 style='text-align:center'>🎓 AI Learning Studio</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center'>Learn to build AI apps for higher education — "
                    "from your very first line of Python to a deployed app.</p>", unsafe_allow_html=True)
        tab_in, tab_up = st.tabs(["🔑 Log in", "✨ Create account"])
        with tab_in:
            with st.form("login"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Log in", type="primary", width="stretch"):
                    if login(u, p):
                        st.rerun()
                    else:
                        st.error("Wrong username or password.")
        with tab_up:
            with st.form("signup"):
                name = st.text_input("Your full name")
                u = st.text_input("Choose a username", help="lowercase letters, numbers, _ or .")
                p = st.text_input("Choose a password", type="password")
                p2 = st.text_input("Repeat password", type="password")
                with st.expander("I am a teacher"):
                    code = st.text_input("Teacher code", type="password",
                                         help="Set TEACHER_CODE in the app's secrets. Teachers can see class progress.")
                if st.form_submit_button("Create account", type="primary", width="stretch"):
                    if p != p2:
                        st.error("Passwords don't match.")
                    else:
                        err = signup(u, name, p, code)
                        if err:
                            st.error(err)
                        else:
                            login(u, p)
                            st.session_state.just_signed_up = True
                            st.rerun()
        st.caption("Your progress is saved to your account. No email or payment needed.")
