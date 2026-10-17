"""Built-in practice datasets (synthetic — generated, not real people)."""
import numpy as np
import pandas as pd


def student_performance(n=240, seed=7):
    rng = np.random.default_rng(seed)
    depts = ["Physics", "Commerce", "History", "Computer Science", "Education"]
    dept = rng.choice(depts, n, p=[0.2, 0.25, 0.15, 0.25, 0.15])
    attendance = np.clip(rng.normal(80, 10, n), 40, 100).round()
    study_hours = np.clip(rng.normal(8, 3, n), 0, 20).round(1)
    internal = np.clip(10 + attendance * 0.25 + study_hours * 0.6 + rng.normal(0, 4, n), 0, 50).round()
    external = np.clip(20 + attendance * 0.35 + study_hours * 1.8 + rng.normal(0, 9, n), 0, 100).round()
    df = pd.DataFrame({
        "roll_no": [f"R{1000+i}" for i in range(n)],
        "dept": dept,
        "gender": rng.choice(["F", "M"], n),
        "first_gen_learner": rng.choice(["Yes", "No"], n, p=[0.35, 0.65]),
        "attendance_pct": attendance,
        "weekly_study_hours": study_hours,
        "internal_50": internal,
        "external_100": external,
    })
    df["total_150"] = df["internal_50"] + df["external_100"]
    df["result"] = np.where((df["external_100"] >= 35) & (df["total_150"] >= 60), "Pass", "Fail")
    absent = rng.choice(n, 6, replace=False)
    df["external_100"] = df["external_100"].astype(object)
    df.loc[absent, "external_100"] = "AB"          # realistic mess for cleaning practice
    df.loc[absent, ["total_150", "result"]] = [np.nan, "Absent"]
    return df


def course_feedback(seed=3):
    rng = np.random.default_rng(seed)
    pos = ["The examples from daily life made the concepts clear.", "Loved the hands-on lab sessions.",
           "The teacher explains patiently and answers every doubt.", "Quizzes every week helped me revise.",
           "Group projects were very useful for learning teamwork."]
    neg = ["Too much content was covered in too little time.", "The slides were hard to read from the back.",
           "I wanted more practice problems before the exam.", "Online materials were uploaded late.",
           "The pace was too fast for first-generation learners like me."]
    mix = ["Good course but the assignments were too long.", "Interesting topics, though the lab equipment often failed.",
           "Helpful teacher; the timetable clashed with other classes."]
    rows = []
    for i in range(80):
        kind = rng.choice(["pos", "neg", "mix"], p=[0.45, 0.3, 0.25])
        text = rng.choice({"pos": pos, "neg": neg, "mix": mix}[kind])
        rating = {"pos": rng.integers(4, 6), "neg": rng.integers(1, 3), "mix": 3}[kind]
        rows.append({"response_id": i + 1, "course": rng.choice(["Research Methods", "Statistics", "Educational Psychology"]),
                     "semester": rng.choice(["Sem 1", "Sem 3"]), "rating_1_5": int(rating), "comment": text})
    return pd.DataFrame(rows)


def enrolment_by_state(seed=11):
    rng = np.random.default_rng(seed)
    states = ["Kerala", "Tamil Nadu", "Karnataka", "Maharashtra", "Uttar Pradesh", "Bihar", "West Bengal", "Gujarat",
              "Rajasthan", "Delhi", "Assam", "Punjab"]
    rows = []
    for s in states:
        for year in range(2019, 2024):
            male = int(rng.integers(200, 3000) * 1000)
            female = int(male * rng.uniform(0.85, 1.25))
            rows.append({"state": s, "year": year, "male_enrolment": male, "female_enrolment": female,
                         "colleges": int(rng.integers(300, 8000)), "ger_pct": round(float(rng.uniform(15, 50)), 1)})
    return pd.DataFrame(rows)


DATASETS = {
    "🎓 Student performance (240 students)": (student_performance,
        "Marks, attendance and study hours by department. Contains 'AB' (absent) values to practise cleaning."),
    "💬 Course feedback (80 comments)": (course_feedback,
        "Ratings and free-text comments — great for asking an LLM to find themes and sentiment."),
    "🗺️ Higher-ed enrolment by state (AISHE-style)": (enrolment_by_state,
        "State × year enrolment and GER. Synthetic data shaped like AISHE tables."),
}

SOURCES = [
    ("Hugging Face Datasets", "https://huggingface.co/datasets", "Text, Q&A, exam and language datasets for AI"),
    ("Kaggle Datasets", "https://www.kaggle.com/datasets", "Thousands of CSVs with example notebooks"),
    ("Open Government Data (India)", "https://data.gov.in", "Official Indian open data"),
    ("AISHE", "https://aishe.gov.in", "All India Survey on Higher Education reports and tables"),
    ("UCI ML Repository", "https://archive.ics.uci.edu", "Classic datasets, incl. student performance"),
    ("Google Dataset Search", "https://datasetsearch.research.google.com", "A search engine for datasets"),
    ("NIRF", "https://www.nirfindia.org", "Institutional ranking data"),
]
