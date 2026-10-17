# 🎓 AI Learning Studio

A self-paced learning platform for teachers and students in higher education. It takes learners from
**"I've never written code"** to **building and deploying their own AI apps**, with a step-by-step AI tutor at every step.

## What's inside

| Page | What it does |
|---|---|
| 🔑 **Login** | Student and teacher accounts (passwords are stored hashed) |
| 📊 **My Dashboard** | Progress, current level, streak, a **skill map** with **strong / developing / needs work** areas, next-step recommendations and an AI weekly study plan |
| 📚 **Classes** | 21 lessons in 4 levels (Absolute Beginner → Advanced). Each lesson has a plain description, Learn → Guided practice (fill the blanks from a list) → Your turn (with a step guide and a symbols/syntax helper) → Quiz → Tutor |
| 🏋️ **Practice Gym** | Smart drills weighted to your weak skills, all 24 code challenges, fresh AI-generated questions, and "explain it back" (Feynman technique) |
| 🧑‍🏫 **Ask the Tutor** | Beginner-friendly tutor that **explains step by step**. Press "I don't know" to start from zero, or ask for a simpler explanation, another example or a quick check. Also lets you build a custom AI study-twin persona |
| 🧪 **Model Lab** | Playground, blind **Arena** (compare two models), class leaderboard and a guide to **Groq, Google AI Studio, Mistral, OpenRouter and Hugging Face** |
| 📈 **Data Lab** | Built-in datasets (student performance, course feedback, AISHE-style enrolment) or your own CSV: explore, clean, chart and ask the AI |
| 🧰 **App Gallery** | 7 ready-to-use apps (quiz generator, rubric feedback, lesson planner, research question refiner, flashcards, marks early-warning, PDF assistant) with **downloadable starter code** |
| 👩‍🏫 **Teacher View** | Class overview, skill heat-map, individual reports, backup and restore |

## Run it on your computer

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # Mac / Linux
pip install -r requirements.txt
streamlit run app.py
```

## Add your API key(s)

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in your keys:

```toml
GROQ_API_KEY = "gsk_..."          # free, no card: console.groq.com/keys
TEACHER_CODE = "choose-a-code"    # anyone signing up with this code becomes a teacher
```

Learners can also paste their own keys in **Profile & API Keys**. Those keys last for the browser session only and are never saved.
Without any key, everything still works except the AI features. The tutor then falls back to the lesson's own guiding questions, and written answers use a self-check rubric.

## Deploy free on Streamlit Community Cloud

1. Push this folder to a GitHub repository. `.gitignore` already keeps `secrets.toml` and the database out.
2. Go to share.streamlit.io, choose **Create app**, then pick your repo and `app.py`.
3. Under **Advanced settings → Secrets**, paste the contents of your `secrets.toml`.
4. Click **Deploy** and share the link.

⚠️ **Data persistence:** on Streamlit Cloud the SQLite database resets when the app restarts (after updates, or when it sleeps for a long time).
Teachers should download a backup from **Teacher View** regularly and restore it after a restart. For a permanent class setup,
move `core/db.py` to a hosted database such as Supabase or Postgres.

⚠️ **Code runner:** learners' practice code runs on the server, with a time limit. For a public link, only share it with your class.
To switch the runner off, set `ALLOW_CODE_RUNNER = "false"`.

## Project structure

```
app.py               login + navigation
core/
  curriculum.py      all lessons, exercises and quizzes (add your own lessons here!)
  db.py              SQLite database
  auth.py            sign-up / login
  llm.py             one helper for 5 AI providers (OpenAI-compatible APIs)
  tutor.py           step-by-step tutor + rubric feedback
  scoring.py         mastery, strengths/weaknesses, recommendations
  runner.py          runs and tests learners' code safely with a timeout
  ui.py              shared widgets: tutor panel, quiz, exercises
  datasets.py        built-in synthetic datasets
views/               one file per page
templates/           standalone starter apps for learners to download
```

## Notes on models

Providers retire models often. Groq retired `llama-3.3-70b-versatile` in August 2026, for example. The app loads each
provider's **live model list**, and you can pick a default in **Profile & API Keys**. The default models are in `core/llm.py`.
