"""
Runs a learner's Python code + the exercise tests in a separate process with a time limit,
so an infinite loop can't freeze the app.

Safety note: on a public deployment, logged-in users can run Python on the server.
Set ALLOW_CODE_RUNNER = false in secrets to switch this off.
"""
import os
import subprocess
import sys
import tempfile

MARKER = "__ALL_TESTS_PASSED__"


def run_code(code, tests="", timeout=15):
    program = code + "\n\n# ---- tests ----\n" + tests + f"\nprint({MARKER!r})\n"
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "student.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(program)
        try:
            p = subprocess.run([sys.executable, "-I", path], capture_output=True, text=True,
                               timeout=timeout, cwd=tmp)
        except subprocess.TimeoutExpired:
            return {"passed": False, "stdout": "", "error": f"⏱️ Your code took longer than {timeout} s. "
                                                            "Is there a loop that never ends?"}
    out = p.stdout.replace(MARKER, "").rstrip()
    passed = p.returncode == 0 and MARKER in p.stdout
    err = ""
    if not passed:
        err = friendly_error(p.stderr)
    return {"passed": passed, "stdout": out, "error": err}


def friendly_error(stderr):
    """Show the useful last line, plus a beginner-friendly explanation."""
    lines = [l for l in stderr.strip().splitlines() if l.strip()]
    last = lines[-1] if lines else "Unknown error"
    line_no = ""
    for l in reversed(lines):
        if 'File "' in l and "student.py" in l and "line" in l:
            line_no = l.split("line")[-1].split(",")[0].strip()
            break
    tips = {
        "AssertionError": "A test failed — your code runs, but the result isn't what was expected yet.",
        "NameError": "You used a name Python doesn't know. Did you fill every ___ blank, and spell variables the same way?",
        "SyntaxError": "Python can't read this line. Check brackets ( ), quotes \" \", colons : and blanks ___.",
        "IndentationError": "Spacing problem. Lines inside if/for/def need 4 spaces more than the line above.",
        "TypeError": "Mixing types — e.g. adding text and a number, or calling something with the wrong inputs.",
        "KeyError": "That key isn't in the dictionary. Check spelling and quotes.",
        "IndexError": "You asked for a list position that doesn't exist (remember counting starts at 0).",
        "ZeroDivisionError": "Division by zero.",
        "ModuleNotFoundError": "A package isn't installed.",
        "AttributeError": "That object doesn't have this method/attribute — check the spelling.",
    }
    tip = next((t for k, t in tips.items() if last.startswith(k)), "")
    where = f" (around line {line_no})" if line_no else ""
    msg = f"**{last}**{where}"
    return msg + (f"\n\n💡 {tip}" if tip else "")
