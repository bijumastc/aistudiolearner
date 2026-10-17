"""Marks analyser & early warning — starter template (NO AI needed).
Run: streamlit run marks_analyzer.py
CSV columns expected: roll_no, attendance, internal, external
Ideas: per-subject comparison, email/WhatsApp message drafts for mentors, trends across semesters.
"""
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Marks Analyser", page_icon="📊")
st.title("📊 Marks Analyser")

up = st.file_uploader("Upload marks CSV", type="csv")
if not up:
    st.info("Upload a CSV with columns: roll_no, attendance, internal, external")
    st.stop()

df = pd.read_csv(up)
for c in ["attendance", "internal", "external"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")       # 'AB' -> NaN

att_cut = st.slider("Attendance threshold", 50, 100, 75)
mark_cut = st.slider("Minimum internal marks", 0, 50, 20)

df["flag"] = ""
df.loc[df["attendance"] < att_cut, "flag"] += "Low attendance; "
df.loc[df["internal"] < mark_cut, "flag"] += "Low internal; "
df.loc[df["external"].isna(), "flag"] += "Absent; "

c1, c2, c3 = st.columns(3)
c1.metric("Students", len(df))
c2.metric("Average internal", round(df["internal"].mean(), 1))
c3.metric("Flagged", int((df["flag"] != "").sum()))

st.bar_chart(df["internal"].value_counts(bins=5).sort_index())
st.subheader("Students who may need support")
st.dataframe(df[df["flag"] != ""])
