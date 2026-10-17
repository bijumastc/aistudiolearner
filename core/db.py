"""
Database layer (SQLite).

SQLite is a single file database — perfect for learning and small classes.
NOTE: On Streamlit Community Cloud the file is reset when the app restarts.
Teachers can download a backup from the Teacher page and restore it later.
"""
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = os.environ.get("LEARNER_DB", os.path.join(os.path.dirname(__file__), "..", "data", "learner.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    username    TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    pw_hash     TEXT NOT NULL,
    salt        TEXT NOT NULL,
    role        TEXT NOT NULL DEFAULT 'student',
    focus       TEXT DEFAULT '',
    goal        TEXT DEFAULT '',
    created_at  TEXT,
    last_seen   TEXT
);
CREATE TABLE IF NOT EXISTS lesson_progress (
    username        TEXT,
    lesson_id       TEXT,
    quiz_best       REAL DEFAULT 0,
    quiz_attempts   INTEGER DEFAULT 0,
    practice_score  REAL DEFAULT 0,
    practice_done   INTEGER DEFAULT 0,
    hints_used      INTEGER DEFAULT 0,
    completed       INTEGER DEFAULT 0,
    updated_at      TEXT,
    PRIMARY KEY (username, lesson_id)
);
CREATE TABLE IF NOT EXISTS skill_attempts (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT,
    skill     TEXT,
    correct   INTEGER,
    total     INTEGER,
    source    TEXT,
    ts        TEXT
);
CREATE TABLE IF NOT EXISTS events (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT,
    kind      TEXT,
    detail    TEXT,
    ts        TEXT
);
CREATE TABLE IF NOT EXISTS exercise_results (
    username  TEXT,
    exid      TEXT,
    lesson_id TEXT,
    score     REAL,
    ts        TEXT,
    PRIMARY KEY (username, exid)
);
CREATE TABLE IF NOT EXISTS arena_votes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT,
    prompt    TEXT,
    model_a   TEXT,
    model_b   TEXT,
    winner    TEXT,
    ts        TEXT
);
"""

TABLES = ["users", "lesson_progress", "skill_attempts", "events", "exercise_results", "arena_votes"]


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def connect():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db():
    with connect() as con:
        con.executescript(SCHEMA)


# ---------------- users ----------------
def get_user(username):
    with connect() as con:
        row = con.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        return dict(row) if row else None


def create_user(username, name, pw_hash, salt, role="student"):
    with connect() as con:
        con.execute(
            "INSERT INTO users (username,name,pw_hash,salt,role,created_at,last_seen) VALUES (?,?,?,?,?,?,?)",
            (username, name, pw_hash, salt, role, now(), now()),
        )


def update_user(username, **fields):
    if not fields:
        return
    cols = ", ".join(f"{k}=?" for k in fields)
    with connect() as con:
        con.execute(f"UPDATE users SET {cols} WHERE username=?", (*fields.values(), username))


def all_users(role=None):
    with connect() as con:
        q = "SELECT username,name,role,focus,created_at,last_seen FROM users"
        rows = con.execute(q + (" WHERE role=?" if role else ""), ((role,) if role else ())).fetchall()
        return [dict(r) for r in rows]


# ---------------- lesson progress ----------------
def get_progress(username):
    with connect() as con:
        rows = con.execute("SELECT * FROM lesson_progress WHERE username=?", (username,)).fetchall()
        return {r["lesson_id"]: dict(r) for r in rows}


def _ensure_row(con, username, lesson_id):
    con.execute(
        "INSERT OR IGNORE INTO lesson_progress (username, lesson_id, updated_at) VALUES (?,?,?)",
        (username, lesson_id, now()),
    )


def record_quiz(username, lesson_id, score, pass_mark=0.6):
    with connect() as con:
        _ensure_row(con, username, lesson_id)
        con.execute(
            """UPDATE lesson_progress
               SET quiz_best = MAX(quiz_best, ?), quiz_attempts = quiz_attempts + 1,
                   completed = CASE WHEN MAX(quiz_best, ?) >= ? THEN 1 ELSE completed END,
                   updated_at = ?
               WHERE username=? AND lesson_id=?""",
            (score, score, pass_mark, now(), username, lesson_id),
        )


def record_exercise(username, lesson_id, exid, score, n_exercises):
    """Keep the best score per exercise; lesson practice score = mean over all its exercises."""
    with connect() as con:
        _ensure_row(con, username, lesson_id)
        con.execute(
            """INSERT INTO exercise_results (username, exid, lesson_id, score, ts) VALUES (?,?,?,?,?)
               ON CONFLICT(username, exid) DO UPDATE SET score = MAX(score, excluded.score), ts = excluded.ts""",
            (username, exid, lesson_id, score, now()),
        )
        total = con.execute("SELECT SUM(score) FROM exercise_results WHERE username=? AND lesson_id=?",
                            (username, lesson_id)).fetchone()[0] or 0
        con.execute(
            "UPDATE lesson_progress SET practice_score=?, practice_done=1, updated_at=? WHERE username=? AND lesson_id=?",
            (total / max(n_exercises, 1), now(), username, lesson_id),
        )


def get_exercise_results(username):
    with connect() as con:
        rows = con.execute("SELECT exid, score FROM exercise_results WHERE username=?", (username,)).fetchall()
        return {r["exid"]: r["score"] for r in rows}


def record_hints(username, lesson_id, hints):
    with connect() as con:
        _ensure_row(con, username, lesson_id)
        con.execute(
            "UPDATE lesson_progress SET hints_used = MAX(hints_used, ?), updated_at=? WHERE username=? AND lesson_id=?",
            (hints, now(), username, lesson_id),
        )


# ---------------- skill drills ----------------
def record_skill_attempt(username, skill, correct, total, source="drill"):
    with connect() as con:
        con.execute(
            "INSERT INTO skill_attempts (username,skill,correct,total,source,ts) VALUES (?,?,?,?,?,?)",
            (username, skill, int(correct), int(total), source, now()),
        )


def get_skill_attempts(username):
    with connect() as con:
        rows = con.execute("SELECT * FROM skill_attempts WHERE username=?", (username,)).fetchall()
        return [dict(r) for r in rows]


# ---------------- events ----------------
def log_event(username, kind, detail=""):
    with connect() as con:
        con.execute("INSERT INTO events (username,kind,detail,ts) VALUES (?,?,?,?)",
                    (username, kind, str(detail)[:300], now()))
        con.execute("UPDATE users SET last_seen=? WHERE username=?", (now(), username))


def get_events(username, limit=200):
    with connect() as con:
        rows = con.execute("SELECT * FROM events WHERE username=? ORDER BY id DESC LIMIT ?",
                           (username, limit)).fetchall()
        return [dict(r) for r in rows]


# ---------------- arena ----------------
def record_vote(username, prompt, model_a, model_b, winner):
    with connect() as con:
        con.execute("INSERT INTO arena_votes (username,prompt,model_a,model_b,winner,ts) VALUES (?,?,?,?,?,?)",
                    (username, prompt[:500], model_a, model_b, winner, now()))


def get_votes():
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT * FROM arena_votes").fetchall()]


# ---------------- backup / restore ----------------
def export_all():
    with connect() as con:
        return json.dumps({t: [dict(r) for r in con.execute(f"SELECT * FROM {t}").fetchall()] for t in TABLES},
                          indent=1)


def import_all(text):
    data = json.loads(text)
    with connect() as con:
        for t in TABLES:
            rows = data.get(t, [])
            if not rows:
                continue
            cols = list(rows[0].keys())
            con.executemany(
                f"INSERT OR REPLACE INTO {t} ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                [tuple(r[c] for c in cols) for r in rows],
            )
