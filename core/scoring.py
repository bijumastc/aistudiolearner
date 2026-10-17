"""
Turns raw attempts into feedback: lesson scores, skill mastery, strengths/weaknesses, next steps.

Lesson score  = 60% best quiz + 40% practice (practice only counts once attempted)
Skill mastery = 70% lesson scores in that skill + 30% Practice-Gym drill accuracy
"""
from datetime import date, datetime, timedelta

from core import db
from core.curriculum import LESSONS, LEVELS, SKILLS, lessons_for_skill

PASS_MARK = 0.6
STRONG = 0.75
WEAK = 0.5


def lesson_score(prog):
    if not prog:
        return None
    q_done = prog["quiz_attempts"] > 0
    p_done = bool(prog["practice_done"])
    if q_done and p_done:
        return 0.6 * prog["quiz_best"] + 0.4 * prog["practice_score"]
    if q_done:
        return prog["quiz_best"]
    if p_done:
        return prog["practice_score"]
    return None


def band(m):
    if m is None:
        return "Not started"
    if m < WEAK:
        return "Needs work"
    if m < STRONG:
        return "Developing"
    return "Strong"


BAND_COLORS = {"Strong": "#2e9e5b", "Developing": "#e0a526", "Needs work": "#d1495b", "Not started": "#9aa0a6"}


def skill_report(username):
    progress = db.get_progress(username)
    drills = db.get_skill_attempts(username)
    report = {}
    for skill in SKILLS:
        lessons = lessons_for_skill(skill)
        scores = [lesson_score(progress.get(l["id"])) for l in lessons]
        scores = [s for s in scores if s is not None]
        done = sum(1 for l in lessons if progress.get(l["id"], {}).get("completed"))
        d = [a for a in drills if a["skill"] == skill]
        correct, total = sum(a["correct"] for a in d), sum(a["total"] for a in d)
        lesson_m = sum(scores) / len(scores) if scores else None
        drill_m = correct / total if total else None
        if lesson_m is not None and drill_m is not None:
            mastery = 0.7 * lesson_m + 0.3 * drill_m
        else:
            mastery = lesson_m if lesson_m is not None else drill_m
        report[skill] = {"mastery": mastery, "band": band(mastery), "lessons_done": done,
                         "lessons_total": len(lessons), "drill_correct": correct, "drill_total": total}
    return report


def strengths_and_weaknesses(report):
    strong = [s for s, r in report.items() if r["band"] == "Strong"]
    weak = [s for s, r in report.items() if r["band"] == "Needs work"]
    developing = [s for s, r in report.items() if r["band"] == "Developing"]
    weak.sort(key=lambda s: report[s]["mastery"])
    developing.sort(key=lambda s: report[s]["mastery"])
    return strong, developing, weak


def current_level(progress):
    for level in sorted(LEVELS):
        ls = [l for l in LESSONS if l["level"] == level]
        done = sum(1 for l in ls if progress.get(l["id"], {}).get("completed"))
        if done / len(ls) < PASS_MARK:
            return level
    return max(LEVELS)


def next_lesson(progress):
    for l in LESSONS:
        if not progress.get(l["id"], {}).get("completed"):
            return l
    return None


def recommendations(username, report, progress):
    """Concrete next steps for each weak / developing skill."""
    recs = []
    _, developing, weak = strengths_and_weaknesses(report)
    for skill in weak + developing:
        lessons = lessons_for_skill(skill)
        scored = [(lesson_score(progress.get(l["id"])), l) for l in lessons]
        attempted = [(s, l) for s, l in scored if s is not None]
        target = min(attempted, key=lambda x: x[0])[1] if attempted else lessons[0]
        p = progress.get(target["id"], {})
        if p and p.get("quiz_best", 0) < PASS_MARK:
            why = f"your best quiz score is {p.get('quiz_best', 0):.0%}"
        elif p and p.get("practice_done") and p.get("practice_score", 0) < 0.7:
            why = "practice exercises needed many hints"
        else:
            why = "this is your lowest-scoring lesson in the skill"
        recs.append({"skill": skill, "lesson": target, "why": why, "band": report[skill]["band"]})
    return recs


def streak(username):
    days = set()
    for e in db.get_events(username, limit=1000):
        try:
            days.add(datetime.fromisoformat(e["ts"]).date())
        except Exception:
            pass
    today = date.today()
    d = today if today in days else today - timedelta(days=1)
    count = 0
    while d in days:
        count += 1
        d -= timedelta(days=1)
    return count, len(days)
