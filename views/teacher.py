"""Teacher view: class progress, skill heat-map, individual reports, backup/restore."""
import pandas as pd
import streamlit as st

from core import auth, db, scoring
from core.curriculum import LESSONS, SKILLS

u = auth.current_user()
if u["role"] != "teacher":
    st.error("Teachers only.")
    st.stop()

st.title("👩‍🏫 Teacher View")
students = db.all_users("student")
if not students:
    st.info("No students yet. Share the app link — students create their own accounts.")

rows, heat = [], []
for s in students:
    prog = db.get_progress(s["username"])
    rep = scoring.skill_report(s["username"])
    done = sum(1 for p in prog.values() if p["completed"])
    qs = [p["quiz_best"] for p in prog.values() if p["quiz_attempts"]]
    _, _, weak = scoring.strengths_and_weaknesses(rep)
    rows.append({"Student": s["name"], "Username": s["username"], "Focus": s["focus"], "Lessons done": done,
                 "Progress": done / len(LESSONS), "Avg quiz": (sum(qs) / len(qs)) if qs else None,
                 "Weakest skill": weak[0] if weak else "—", "Last seen": (s["last_seen"] or "")[:16].replace("T", " ")})
    heat.append({"Student": s["name"], **{sk: (rep[sk]["mastery"] * 100 if rep[sk]["mastery"] is not None else None)
                                         for sk in SKILLS}})

if rows:
    df = pd.DataFrame(rows)
    m1, m2, m3 = st.columns(3)
    m1.metric("Students", len(df))
    m2.metric("Avg lessons done", f"{df['Lessons done'].mean():.1f} / {len(LESSONS)}")
    m3.metric("Avg quiz", f"{df['Avg quiz'].dropna().mean():.0%}" if df["Avg quiz"].notna().any() else "—")
    st.subheader("Class overview")
    st.dataframe(df, hide_index=True, width="stretch", column_config={
        "Progress": st.column_config.ProgressColumn(min_value=0, max_value=1, format="%.0f%%"),
        "Avg quiz": st.column_config.NumberColumn(format="%.2f")})

    st.subheader("Skill heat-map (mastery %)")
    st.caption("Blank = not started. Columns that are red for many students show topics to re-teach.")
    hm = pd.DataFrame(heat).set_index("Student")
    st.dataframe(hm.style.background_gradient(cmap="RdYlGn", vmin=0, vmax=100, axis=None).format("{:.0f}", na_rep=""),
                 width="stretch")
    class_avg = hm.mean().dropna().sort_values()
    if not class_avg.empty:
        st.markdown(f"**Class's weakest skills:** {', '.join(f'{k} ({v:.0f}%)' for k, v in class_avg.head(3).items())}")

    st.subheader("Individual report")
    who = st.selectbox("Student", df["Username"], format_func=lambda x: df.set_index("Username").loc[x, "Student"])
    prog = db.get_progress(who)
    lrows = [{"Lesson": f"{l['id']} {l['title']}", "Skill": l["skill"],
              "Quiz best": prog.get(l["id"], {}).get("quiz_best"), "Attempts": prog.get(l["id"], {}).get("quiz_attempts", 0),
              "Practice": prog.get(l["id"], {}).get("practice_score"), "Hints": prog.get(l["id"], {}).get("hints_used", 0),
              "Done": "✅" if prog.get(l["id"], {}).get("completed") else ""} for l in LESSONS]
    st.dataframe(pd.DataFrame(lrows), hide_index=True, width="stretch")

st.subheader("💾 Backup & restore")
st.caption("On Streamlit Community Cloud the database resets when the app restarts. Download a backup regularly.")
c1, c2 = st.columns(2)
c1.download_button("⬇️ Download full backup (JSON)", db.export_all(), "learning_studio_backup.json", "application/json")
up = c2.file_uploader("Restore from backup", type="json")
if up and c2.button("Restore now", type="primary"):
    db.import_all(up.read().decode("utf-8"))
    st.success("Restored.")
