"""
The AI tutor — a patient, beginner-friendly teacher.

It EXPLAINS step by step (it does not answer questions with more questions).
When a learner says "I don't know", it starts from zero and teaches the idea in small numbered steps.
Buttons in the chat let the learner ask for a simpler explanation, another example, or a quick check.
"""
import re

from core import llm

TEACHING_STYLE = """How to teach:
- Explain STEP BY STEP using numbered steps (Step 1, Step 2, …). One small idea per step. Short, simple sentences.
- Assume the learner is an absolute beginner. Define every technical word the first time you use it
  (e.g. "a variable is a labelled box that stores a value").
- Use an everyday analogy, ideally from the learner's subject.
- Show tiny code examples in ```python blocks``` and explain what EACH line does, in plain words.
- When code is involved, point out every symbol the learner must type — brackets ( ) [ ] { }, quotes " ",
  colon :, equals = vs double equals ==, underscore _, and the 4-space indentation.
- If the learner says "I don't know", "not sure", "confused", "no idea" or similar: do NOT ask them questions back.
  Teach the idea from the very beginning, step by step.
- If they share an error message, explain in plain words what it means, which line is wrong, and exactly how to fix it.
- If they are working on a practice exercise, guide them piece by piece: show the next small piece of code,
  explain it, and tell them where to type it. Give the full code only if they ask for it.
- End with ONE short, easy "✅ Try this:" task so they can check their understanding.
- Be warm and encouraging. Never make the learner feel slow. Use markdown headings sparingly."""

MODES = {
    "explain": "",
    "dont_know": "The learner doesn't know where to start. Teach this topic from zero, step by step, with a tiny example.",
    "simpler": "Explain the last point again, MUCH more simply: shorter sentences, a new everyday analogy, no jargon at all.",
    "example": "Give one new, fully worked example (with code if relevant), explaining each line, then a similar mini-task.",
    "check": "Check understanding gently: ask 2 short, easy questions (numbered). Tell the learner to reply with their answers; "
             "when they do, mark them kindly and explain anything they missed.",
}

DONT_KNOW = re.compile(r"\b(i\s*don'?t\s*know|dont\s*know|idk|no\s*idea|not\s*sure|confus|lost|don'?t\s*understand|"
                       r"didn'?t\s*understand|what\s*does\s*this\s*mean|help)\b", re.I)


def system_prompt(user, lesson=None, persona=None, extra_context="", mode="explain"):
    focus = (user or {}).get("focus") or "general higher education"
    name = (user or {}).get("name", "the learner").split()[0]
    base = persona or (
        "You are a warm, patient teacher in a course that teaches university teachers and students to build AI apps "
        "with Python and Streamlit. Most learners are absolute beginners."
    )
    lesson_txt = ""
    if lesson:
        lesson_txt = (f"\nCurrent lesson: {lesson['title']} (skill: {lesson['skill']}).\n"
                      f"Objectives: {'; '.join(lesson['objectives'])}.\n"
                      f"Lesson notes (use them, stay consistent with them):\n{lesson['learn'][:2500]}\n")
    mode_txt = MODES.get(mode, "")
    return (f"{base}\n\nLearner: {name}. Their subject / focus: {focus}. Use examples from that subject where helpful.\n"
            f"{lesson_txt}\n{extra_context}\n\n{TEACHING_STYLE}\n"
            + (f"\nRIGHT NOW: {mode_txt}" if mode_txt else ""))


def reply(history, user, lesson=None, mode="explain", persona=None, extra_context=""):
    if mode == "explain" and history and DONT_KNOW.search(history[-1]["content"]):
        mode = "dont_know"
    msgs = [{"role": "system", "content": system_prompt(user, lesson, persona, extra_context, mode)}]
    msgs += history[-14:]
    return llm.ask(msgs, temperature=0.4, max_tokens=1800)


def offline_help(lesson):
    """No API key: give a step-by-step summary built from the lesson itself."""
    if not lesson:
        return ("I need an AI key to answer free questions. Add your free Groq key in **Profile & API Keys**. "
                "Meanwhile, open a lesson's **Learn** tab — it explains everything step by step.")
    steps = "\n".join(f"**Step {i+1}.** {o}." for i, o in enumerate(lesson["objectives"]))
    code = re.search(r"```python\n(.*?)```", lesson["learn"], re.S)
    example = f"\n\n**Example from the lesson:**\n```python\n{code.group(1)}```" if code else ""
    return (f"Here's what this lesson teaches, step by step:\n\n{lesson.get('about', '')}\n\n{steps}{example}\n\n"
            "📖 The **Learn** tab explains each step in detail. "
            "*(Add a free Groq key in Profile & API Keys and I can explain anything you ask, in your own words.)*")


def grade_reflection(text, rubric, prompt, user):
    """AI feedback on an open answer against a rubric. Returns dict or None."""
    rubric_txt = "\n".join(f"{i+1}. {r}" for i, r in enumerate(rubric))
    msgs = [
        {"role": "system", "content": "You are a supportive teacher giving clear, beginner-friendly feedback. Output only JSON."},
        {"role": "user", "content": f"""Task given to the learner:
{prompt}

Rubric (each criterion is met or not met):
{rubric_txt}

Learner's answer:
\"\"\"{text}\"\"\"

Return JSON: {{"met": [list of criterion numbers met], "strength": "one specific strength",
"improve": "one specific, kind suggestion, with an example sentence they could add",
"model_answer": "a short, simple model answer (3-5 sentences) the learner can compare with"}}"""},
    ]
    raw = llm.ask(msgs, temperature=0.2, json_mode=True, max_tokens=1200)
    if raw is None:
        return None
    try:
        data = llm.extract_json(raw)
        met = [int(m) for m in data.get("met", []) if str(m).isdigit() and 1 <= int(m) <= len(rubric)]
        data["met"] = sorted(set(met))
        data["score"] = len(data["met"]) / len(rubric)
        return data
    except Exception:
        return {"met": [], "score": 0.0, "strength": "", "improve": raw[:500], "model_answer": ""}
