"""
The course content.

Structure of every lesson (scaffolding = I do → We do → You do → Check):
  learn     : explanation + worked example                  (I do)
  practice  : list of exercises; the first is guided          (We do), then independent (You do)
              kind = "code"    -> auto-tested Python with a hint ladder
              kind = "build"   -> do it on your computer, tick the checklist, optional AI review
              kind = "reflect" -> write an answer, AI (or a self-check rubric) gives feedback
  quiz      : multiple choice, auto-graded, explanations       (Check)
  think     : Socratic questions the tutor can start with

Teachers can add lessons by copying a block below.
"""
from textwrap import dedent as d

LEVELS = {
    0: ("🌱 Level 0 · Absolute Beginner", "Never coded before? Start here."),
    1: ("🟢 Level 1 · Beginner", "Build and share your first web app."),
    2: ("🟡 Level 2 · Intermediate", "Talk to AI models from code, reliably."),
    3: ("🔴 Level 3 · Advanced", "Build, evaluate and deploy real higher-education AI apps."),
}

SKILLS = ["Foundations", "Python", "Dev Tools & Deploy", "Streamlit", "Data",
          "LLM Concepts", "Platforms & APIs", "Prompting", "RAG & Apps", "Responsible AI"]

LESSONS = [
# =============================================================================
# LEVEL 0
# =============================================================================
{
"id": "L0-1", "level": 0, "skill": "Foundations", "minutes": 20,
"title": "What are AI, LLMs and APIs?",
"objectives": ["Explain what a Large Language Model (LLM) does in one sentence",
               "Explain what an API and an API key are",
               "Know what we will build in this course"],
"learn": d("""
### The big picture
Imagine a **very well-read assistant** who has read millions of books and web pages. You give it some text
(a **prompt**) and it continues the text in the most likely, useful way. That is a **Large Language Model (LLM)**.

* It **predicts the next word** (actually the next *token*, a piece of a word) again and again.
* It does **not look things up** unless we give it documents — so it can be confidently wrong ("hallucinate").

### Where do the models live?
Companies such as **Groq, Google, Mistral** run these models on powerful computers in the cloud.
We talk to them through an **API** (Application Programming Interface) — a "service window" where our program
hands over a request and receives a reply.

| Everyday analogy | Tech word |
|---|---|
| Library service counter | API |
| Your library card | API key (keep it secret!) |
| The question slip you hand in | Prompt / request |
| The book the librarian brings | Response |

### What will *you* build?
Small web apps for teaching and research: quiz generators, feedback assistants, PDF study helpers and an
AI study companion — written in **Python** and shown on the web with **Streamlit**.
"""),
"think": ["If an LLM only predicts the next word, why can it still answer questions about your subject?",
          "Why do you think an API key must be kept secret, like an ATM PIN?"],
"practice": [
    {"kind": "reflect", "title": "Explain it to a colleague",
     "prompt": "In 3–5 sentences, explain to a fellow teacher what an LLM is and what an API key is. "
               "Use one analogy from your own subject or daily life.",
     "rubric": ["Says an LLM predicts/generates text from patterns learned from lots of text",
                "Mentions that it can be wrong / hallucinate",
                "Explains an API as a way for programs to request a service",
                "Explains that an API key identifies you and must stay secret",
                "Uses a clear analogy"],
     "hints": ["Start with: 'An LLM is like…'", "Use the library-counter analogy, or invent your own.",
               "Finish with one sentence about why the key is secret."]},
],
"quiz": [
    {"q": "What does an LLM fundamentally do?",
     "options": ["Searches Google for the answer", "Predicts the next piece of text, again and again",
                 "Copies answers from a fixed database", "Runs Python code"],
     "answer": 1, "why": "LLMs generate text token by token based on patterns learned in training."},
    {"q": "An API key is most like…",
     "options": ["A public website address", "Your secret library card / PIN", "A Python variable name", "A model's name"],
     "answer": 1, "why": "It identifies you to the provider and allows usage on your account — keep it secret."},
    {"q": "Why can an LLM give a confident but wrong answer?",
     "options": ["It is lazy", "It generates plausible text and doesn't check facts unless given sources",
                 "The internet is slow", "API keys expire"],
     "answer": 1, "why": "This is called hallucination. Giving it trusted documents (RAG, Level 3) reduces it."},
    {"q": "In this course, which tool shows our Python program as a web page?",
     "options": ["Excel", "Streamlit", "PowerPoint", "Docker"], "answer": 1,
     "why": "Streamlit turns a Python script into an interactive web app."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L0-2", "level": 0, "skill": "Python", "minutes": 30,
"title": "Python 1: print, variables and numbers",
"objectives": ["Store values in variables", "Use text (str) and numbers (int, float)", "Build sentences with f-strings"],
"learn": d("""
### Variables are labelled boxes
```python
name = "Asha"        # text  -> str  (always in quotes)
age = 21             # whole number -> int
cgpa = 8.4           # decimal -> float
```
The `=` sign means **"put the value on the right into the box on the left"** — it is not "equals" as in maths.

### Showing results
```python
print(name)                              # Asha
print("Next year", name, "will be", age + 1)
```

### f-strings: sentences with variables inside
Put an `f` before the quotes and variables inside `{curly brackets}`:
```python
message = f"{name} has a CGPA of {cgpa}"
print(message)        # Asha has a CGPA of 8.4
```

### Maths
`+  -  *  /` work as expected. `round(55.333, 1)` gives `55.3`.

**Worked example — percentage**
```python
obtained = 68
maximum = 80
percent = round(obtained / maximum * 100, 1)
print(f"Score: {percent}%")   # Score: 85.0%
```
"""),
"think": ["What is the difference between `age = 21` and `age = \"21\"`? What would `age + 1` do in each case?",
          "Why might we want to store a value in a variable instead of typing the number every time?"],
"practice": [
    {"kind": "code", "title": "We do: fill in the blanks",
     "prompt": "Replace every `___` so that `greeting` becomes exactly **Hello Asha, you are 21**. "
               "`age` must be a number, not text.",
     "starter": d("""
        name = ___
        age = ___
        greeting = f"Hello {___}, you are {___}"
        print(greeting)
        """),
     "tests": d("""
        assert name == "Asha", "name should be the text 'Asha' (with quotes)"
        assert isinstance(age, int) and age == 21, "age should be the number 21 (no quotes)"
        assert greeting == "Hello Asha, you are 21", f"greeting is '{greeting}'"
        """),
     "hints": ["Text needs quotes: `name = \"Asha\"`. Numbers don't: `age = 21`.",
               "Inside the f-string, write the *variable names* in the curly brackets.",
               "`greeting = f\"Hello {name}, you are {age}\"`"],
     "solution": d("""
        name = "Asha"
        age = 21
        greeting = f"Hello {name}, you are {age}"
        print(greeting)
        """)},
    {"kind": "code", "title": "You do: marks calculator",
     "prompt": "A student scored `internal = 32` and `external = 51`. The maximum is 150.\n\n"
               "Create `total` (sum of both) and `percent` (percentage of 150, **rounded to 1 decimal**). "
               "Then print a sentence like `Total 83 = 55.3%`.",
     "starter": d("""
        internal = 32
        external = 51
        # your code here
        """),
     "tests": d("""
        assert total == 83, f"total should be 83, got {total}"
        assert percent == 55.3, f"percent should be 55.3, got {percent}"
        """),
     "hints": ["`total = internal + external`", "Percentage = total ÷ maximum × 100",
               "`percent = round(total / 150 * 100, 1)`"],
     "solution": d("""
        internal = 32
        external = 51
        total = internal + external
        percent = round(total / 150 * 100, 1)
        print(f"Total {total} = {percent}%")
        """)},
],
"quiz": [
    {"q": "What does `x = 5` do?", "options": ["Checks if x equals 5", "Stores 5 in a box called x",
                                             "Prints 5", "Creates an error"], "answer": 1,
     "why": "A single = assigns a value. (== is used for comparing.)"},
    {"q": "What is the type of `\"21\"`?", "options": ["int", "float", "str", "bool"], "answer": 2,
     "why": "Anything inside quotes is text (str), even digits."},
    {"q": "What does `print(f\"Hi {name}\")` print if name = \"Ravi\"?",
     "options": ["Hi {name}", "Hi name", "Hi Ravi", "Error"], "answer": 2, "why": "The f-string replaces {name} with its value."},
    {"q": "`round(7 / 3, 2)` gives…", "options": ["2", "2.33", "2.3", "7/3"], "answer": 1,
     "why": "7/3 = 2.3333…, rounded to 2 decimals = 2.33."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L0-3", "level": 0, "skill": "Python", "minutes": 35,
"title": "Python 2: lists, loops and decisions",
"objectives": ["Store many values in a list", "Repeat actions with a for-loop", "Make decisions with if / elif / else"],
"learn": d("""
### Lists hold many values
```python
marks = [45, 78, 62, 90, 38]
print(marks[0])      # 45  (counting starts at 0!)
print(len(marks))    # 5
marks.append(71)     # add to the end
```

### Loops repeat work
```python
for m in marks:          # m takes each value in turn
    print(m)
```
**Indentation (4 spaces) matters** — it shows which lines are inside the loop.

### Decisions
```python
if m >= 75:
    print("Distinction")
elif m >= 40:
    print("Pass")
else:
    print("Fail")
```

### Worked example — class average
```python
total = 0
for m in marks:
    total = total + m
average = total / len(marks)
```
(Python also has shortcuts: `sum(marks)`, `max(marks)`, `min(marks)`.)
"""),
"think": ["If `marks = [45, 78]`, what is `marks[2]`? What do you predict will happen?",
          "Why does Python need indentation? What would be confusing without it?"],
"practice": [
    {"kind": "code", "title": "We do: count the passes",
     "prompt": "Count how many marks are **40 or more**. Fill in the two blanks.",
     "starter": d("""
        marks = [45, 78, 62, 90, 38]
        passed = 0
        for m in marks:
            if ___:
                passed = ___
        print(passed)
        """),
     "tests": "assert passed == 4, f'passed should be 4, got {passed}'\n",
     "hints": ["The condition compares `m` with 40.", "`m >= 40`", "Add one to the counter: `passed = passed + 1`"],
     "solution": d("""
        marks = [45, 78, 62, 90, 38]
        passed = 0
        for m in marks:
            if m >= 40:
                passed = passed + 1
        print(passed)
        """)},
    {"kind": "code", "title": "You do: convert marks to grades",
     "prompt": "Build a list `grades` with one letter per mark: **'A'** if mark ≥ 75, **'B'** if mark ≥ 50, otherwise **'C'**.",
     "starter": d("""
        marks = [45, 78, 62, 90, 38]
        grades = []
        # loop over marks and append a letter for each
        """),
     "tests": "assert grades == ['C', 'A', 'B', 'A', 'C'], f'got {grades}'\n",
     "hints": ["Use `for m in marks:` then `if / elif / else`.", "Inside each branch: `grades.append(\"A\")` etc.",
               "Check the biggest condition (≥ 75) first, then ≥ 50."],
     "solution": d("""
        marks = [45, 78, 62, 90, 38]
        grades = []
        for m in marks:
            if m >= 75:
                grades.append("A")
            elif m >= 50:
                grades.append("B")
            else:
                grades.append("C")
        """)},
],
"quiz": [
    {"q": "`marks = [10, 20, 30]`. What is `marks[1]`?", "options": ["10", "20", "30", "Error"], "answer": 1,
     "why": "Lists start counting at 0, so index 1 is the second item."},
    {"q": "What does indentation inside a for-loop show?", "options": ["Nothing, it's decoration",
     "Which lines repeat inside the loop", "Comments", "The loop's speed"], "answer": 1,
     "why": "Indented lines belong to the loop (or if-block) above."},
    {"q": "Which is checked first in if / elif / else?", "options": ["else", "the last elif", "if", "all at once"],
     "answer": 2, "why": "Python checks top to bottom and stops at the first True condition."},
    {"q": "Which adds 50 to the end of a list `x`?", "options": ["x.add(50)", "x.append(50)", "x + 50", "append(x, 50)"],
     "answer": 1, "why": "Lists have an .append() method."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L0-4", "level": 0, "skill": "Python", "minutes": 40,
"title": "Python 3: functions and dictionaries",
"objectives": ["Write reusable functions with def and return", "Store labelled data in dictionaries",
               "Combine loops, ifs, functions and dictionaries"],
"learn": d("""
### Functions = reusable recipes
```python
def percentage(obtained, maximum):
    return round(obtained / maximum * 100, 1)

print(percentage(68, 80))   # 85.0
print(percentage(30, 50))   # 60.0
```
`def` defines it, the names in brackets are **inputs (parameters)**, `return` sends back the **output**.

### Dictionaries = labelled boxes
```python
student = {"name": "Asha", "dept": "Physics", "marks": 82}
print(student["name"])          # Asha
student["marks"] = 85           # change a value

class_marks = {"Asha": 82, "Ravi": 35, "Meera": 67}
for name, mark in class_marks.items():
    print(name, mark)
```
Dictionaries are everywhere in AI apps — **API requests and responses are dictionaries (JSON)**.
"""),
"think": ["Why is a function better than copying the same 5 lines in three places?",
          "When would you choose a dictionary instead of a list?"],
"practice": [
    {"kind": "code", "title": "We do: a grade function",
     "prompt": "Complete `grade(mark)` so it returns 'A' (≥ 75), 'B' (≥ 50) or 'C'.",
     "starter": d("""
        def grade(mark):
            if mark >= 75:
                return ___
            elif ___:
                return "B"
            else:
                return ___
        """),
     "tests": d("""
        assert grade(80) == "A" and grade(75) == "A", "75 and above should be A"
        assert grade(60) == "B" and grade(50) == "B", "50–74 should be B"
        assert grade(10) == "C", "below 50 should be C"
        """),
     "hints": ["`return` is followed by the value to send back, e.g. `return \"A\"`.",
               "The elif condition is `mark >= 50`.", "Last return is `\"C\"`."],
     "solution": d("""
        def grade(mark):
            if mark >= 75:
                return "A"
            elif mark >= 50:
                return "B"
            else:
                return "C"
        """)},
    {"kind": "code", "title": "You do: class report",
     "prompt": "Write `class_report(marks)` where `marks` is a dictionary like `{\"Asha\": 82, \"Ravi\": 35}`.\n\n"
               "Return a dictionary with:\n* `\"average\"` – mean mark rounded to 1 decimal\n"
               "* `\"topper\"` – name with the highest mark\n* `\"failed\"` – **sorted** list of names with mark < 40",
     "starter": d("""
        def class_report(marks):
            # your code here
            return {"average": 0, "topper": "", "failed": []}
        """),
     "tests": d("""
        r = class_report({"Asha": 82, "Ravi": 35, "Meera": 67, "John": 20})
        assert r["average"] == 51.0, f"average: expected 51.0, got {r['average']}"
        assert r["topper"] == "Asha", f"topper: expected Asha, got {r['topper']}"
        assert r["failed"] == ["John", "Ravi"], f"failed: expected ['John', 'Ravi'], got {r['failed']}"
        """),
     "hints": ["`sum(marks.values()) / len(marks)` gives the mean.",
               "`max(marks, key=marks.get)` returns the key with the largest value.",
               "Build failed with a loop over `marks.items()` and `if mark < 40`, then `sorted(...)`."],
     "solution": d("""
        def class_report(marks):
            average = round(sum(marks.values()) / len(marks), 1)
            topper = max(marks, key=marks.get)
            failed = sorted(name for name, m in marks.items() if m < 40)
            return {"average": average, "topper": topper, "failed": failed}
        """)},
],
"quiz": [
    {"q": "What does `return` do in a function?", "options": ["Prints the value", "Sends a value back to whoever called it",
     "Stops Python", "Repeats the function"], "answer": 1, "why": "return gives the result back; print only shows it."},
    {"q": "`s = {\"name\": \"Asha\"}`. How do you get \"Asha\"?", "options": ["s[0]", "s.name", "s[\"name\"]", "s(name)"],
     "answer": 2, "why": "Dictionaries are accessed by key in square brackets."},
    {"q": "Why do AI apps use dictionaries so much?", "options": ["They are faster than lists always",
     "API requests and responses are JSON, which maps to dictionaries", "Streamlit requires them", "They can't be changed"],
     "answer": 1, "why": "JSON objects ↔ Python dictionaries."},
    {"q": "In `def area(l, w):`, what are l and w?", "options": ["Return values", "Parameters (inputs)", "Global constants", "Errors"],
     "answer": 1, "why": "Names in the brackets are the inputs the function receives."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L0-5", "level": 0, "skill": "Dev Tools & Deploy", "minutes": 30,
"title": "Your workspace: VS Code, terminal, venv and pip",
"objectives": ["Install Python and VS Code", "Create and activate a virtual environment",
               "Install packages with pip and save them in requirements.txt"],
"learn": d("""
### The four tools
| Tool | What it is | Analogy |
|---|---|---|
| **VS Code** | Where you write code | Your notebook |
| **Terminal** | Where you type commands | Talking to the computer directly |
| **venv** | A private box of packages for one project | A separate cupboard per course |
| **pip** | Installs Python packages | The library's book-ordering desk |

### Step by step (do this on your computer)
```bash
# 1. make a folder and enter it
mkdir my-first-app
cd my-first-app

# 2. create the virtual environment (once)
python -m venv .venv

# 3. switch it ON (every time you open a new terminal)
.venv\\Scripts\\activate          # Windows
source .venv/bin/activate        # Mac / Linux

# 4. install packages
pip install streamlit pandas requests

# 5. remember what you installed (the cloud reads this file)
pip freeze > requirements.txt
```
✅ It worked if your terminal line starts with **(.venv)**.

**Common errors**
* *'python' is not recognized* → reinstall Python and tick **"Add Python to PATH"** (Windows).
* *running scripts is disabled* (Windows PowerShell) → run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.
"""),
"think": ["What problem would happen if two projects needed different versions of the same package without venv?",
          "Why does the cloud need requirements.txt?"],
"practice": [
    {"kind": "build", "title": "Set up your computer",
     "prompt": "Do these steps on your own computer. Tick each one when it works. If you get an error, copy the "
               "message into the tutor — it will help you read it.",
     "checklist": ["Installed Python 3.11+ (python --version works)", "Installed VS Code with the Python extension",
                   "Created a project folder and a .venv inside it", "Activated .venv — the prompt shows (.venv)",
                   "pip install streamlit worked", "streamlit hello opened in the browser"],
     "hints": ["Download Python from python.org; on Windows tick 'Add Python to PATH'.",
               "In VS Code: Terminal → New Terminal opens a terminal in your folder.",
               "If activation fails on Windows, run the Set-ExecutionPolicy command from the lesson once."]},
],
"quiz": [
    {"q": "What is a virtual environment for?", "options": ["Running code faster", "Keeping each project's packages separate",
     "Hiding your API key", "Connecting to the internet"], "answer": 1, "why": "Each venv has its own packages, so projects don't clash."},
    {"q": "How can you tell your venv is active?", "options": ["VS Code turns blue", "The terminal prompt starts with (.venv)",
     "A pop-up appears", "Python restarts"], "answer": 1, "why": "Activation adds the environment name to your prompt."},
    {"q": "What does `pip freeze > requirements.txt` do?", "options": ["Deletes packages", "Saves the list of installed packages to a file",
     "Freezes your computer", "Uploads to GitHub"], "answer": 1, "why": "Others (and Streamlit Cloud) install the same list from it."},
    {"q": "Which command installs Streamlit?", "options": ["python streamlit", "install streamlit", "pip install streamlit", "venv streamlit"],
     "answer": 2, "why": "pip install <package>."},
],
},
# =============================================================================
# LEVEL 1
# =============================================================================
{
"id": "L1-1", "level": 1, "skill": "Streamlit", "minutes": 40,
"title": "Streamlit basics: widgets and layout",
"objectives": ["Run a Streamlit app", "Use text, number, slider and select widgets", "Arrange things with columns, tabs and sidebar"],
"learn": d("""
### Your first app (`app.py`)
```python
import streamlit as st

st.title("Attendance Checker")
name = st.text_input("Student name")
attended = st.number_input("Classes attended", 0, 100, 40)
total = st.number_input("Total classes", 1, 100, 50)

percent = attended / total * 100
st.metric("Attendance", f"{percent:.1f}%")
if percent < 75:
    st.error(f"{name} is below the 75% requirement")
else:
    st.success(f"{name} is eligible")
```
Run it with `streamlit run app.py`.

### Every widget **returns a value** you can use in Python
`st.text_input` → text, `st.slider` → number, `st.selectbox` → chosen option, `st.button` → True only on the click.

### Layout
```python
col1, col2 = st.columns(2)
col1.write("left");  col2.write("right")

tab1, tab2 = st.tabs(["Data", "Chart"])
with tab1:
    st.write("inside tab 1")

st.sidebar.selectbox("Department", ["Physics", "Commerce"])
```
"""),
"think": ["The app has no 'Calculate' button, yet the percentage updates. How do you think Streamlit does that?",
          "Which widget would you use for choosing one of 5 departments? Why not a text box?"],
"practice": [
    {"kind": "build", "title": "Build the Attendance Checker",
     "prompt": "Copy the example into `app.py` on your computer, run it, then **improve it**: add a sidebar with the "
               "course name, put the inputs in two columns, and show how many more classes are needed to reach 75%.",
     "checklist": ["App runs with streamlit run app.py", "Inputs are arranged in two columns", "Sidebar shows a course name",
                   "Shows classes still needed to reach 75%"],
     "hints": ["`c1, c2 = st.columns(2)` then `attended = c1.number_input(...)`.",
               "Classes needed: keep adding 1 to both attended and total until the percentage ≥ 75 (a while-loop), or solve the equation.",
               "Formula: needed = max(0, ceil((0.75*total - attended) / 0.25)) — `from math import ceil`."]},
],
"quiz": [
    {"q": "What does `st.slider(...)` give back to your code?", "options": ["Nothing", "The number the user selected",
     "A chart", "A True/False"], "answer": 1, "why": "Every widget returns its current value."},
    {"q": "How do you run a Streamlit app?", "options": ["python app.py", "streamlit run app.py", "run app.py", "pip app.py"],
     "answer": 1, "why": "streamlit run starts the web server and opens the browser."},
    {"q": "Which creates side-by-side areas?", "options": ["st.tabs", "st.columns", "st.sidebar", "st.expander"], "answer": 1,
     "why": "st.columns splits the page horizontally."},
    {"q": "`st.button('Go')` returns True…", "options": ["Always", "Only during the run right after it is clicked",
     "After two clicks", "Never"], "answer": 1, "why": "Buttons are True only for the one rerun the click triggers (next lesson!)."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L1-2", "level": 1, "skill": "Streamlit", "minutes": 40,
"title": "Reruns and session_state (why data 'vanishes')",
"objectives": ["Explain Streamlit's top-to-bottom rerun model", "Keep data between reruns with st.session_state",
               "Build a counter and a to-do list"],
"learn": d("""
### The rerun model
Every time a learner touches a widget, Streamlit **runs your whole file again from the top**.
So normal variables are **reset** every time:
```python
count = 0                      # runs again on every click -> back to 0!
if st.button("Add"):
    count += 1
st.write(count)                # only ever 0 or 1
```

### session_state = memory that survives reruns
```python
if "count" not in st.session_state:   # only the FIRST time
    st.session_state.count = 0

if st.button("Add"):
    st.session_state.count += 1

st.write(st.session_state.count)      # 1, 2, 3, ...
```
Think of `st.session_state` as a **dictionary that Streamlit keeps for each visitor**.
Chat apps store the whole conversation in it — that's how a chatbot "remembers".
"""),
"think": ["If session_state is a dictionary per visitor, what happens when two students use your app at the same time?",
          "Why do we check `if 'count' not in st.session_state` before setting it to 0?"],
"practice": [
    {"kind": "code", "title": "We do: simulate a rerun",
     "prompt": "Here `state` plays the role of `st.session_state` (a dictionary) and calling `run_app` is one rerun. "
               "Make the counter remember its value: create `count` only if it is missing, and add 1 when `clicked` is True.",
     "starter": d("""
        def run_app(state, clicked):
            if ___ not in state:
                state["count"] = ___
            if clicked:
                state["count"] = ___
            return state["count"]
        """),
     "tests": d("""
        s = {}
        assert run_app(s, False) == 0, "first run without a click should show 0"
        assert run_app(s, True) == 1, "after one click: 1"
        assert run_app(s, True) == 2, "after two clicks: 2 (does it remember?)"
        assert run_app(s, False) == 2, "a rerun without a click must keep 2"
        """),
     "hints": ["The key is the text \"count\".", "Start the counter at 0.", "`state[\"count\"] + 1`"],
     "solution": d("""
        def run_app(state, clicked):
            if "count" not in state:
                state["count"] = 0
            if clicked:
                state["count"] = state["count"] + 1
            return state["count"]
        """)},
    {"kind": "code", "title": "You do: a to-do list that remembers",
     "prompt": "Write `add_task(state, task)`. It should create `state[\"tasks\"]` as an empty list if missing, "
               "**ignore** empty text (after stripping spaces) and **duplicates**, otherwise append the stripped task. "
               "Return the list.",
     "starter": d("""
        def add_task(state, task):
            # your code here
            return state.get("tasks", [])
        """),
     "tests": d("""
        s = {}
        assert add_task(s, "Read chapter 2") == ["Read chapter 2"]
        assert add_task(s, "   ") == ["Read chapter 2"], "blank tasks must be ignored"
        assert add_task(s, "Read chapter 2") == ["Read chapter 2"], "duplicates must be ignored"
        assert add_task(s, "  Make quiz ") == ["Read chapter 2", "Make quiz"], "tasks should be stripped of spaces"
        """),
     "hints": ["Start like the counter: `if \"tasks\" not in state: state[\"tasks\"] = []`.",
               "`task = task.strip()` removes spaces at both ends.",
               "Only append when `task and task not in state[\"tasks\"]`."],
     "solution": d("""
        def add_task(state, task):
            if "tasks" not in state:
                state["tasks"] = []
            task = task.strip()
            if task and task not in state["tasks"]:
                state["tasks"].append(task)
            return state["tasks"]
        """)},
],
"quiz": [
    {"q": "When does Streamlit rerun your script?", "options": ["Only once", "Every time a widget is changed or clicked",
     "Every 10 seconds", "Only when you save the file"], "answer": 1, "why": "Each interaction triggers a full top-to-bottom rerun."},
    {"q": "Why does a normal variable 'forget' its value?", "options": ["Python has a bug", "Its assignment runs again on every rerun",
     "The browser deletes it", "It's too large"], "answer": 1, "why": "`count = 0` executes again on every rerun."},
    {"q": "What is st.session_state most like?", "options": ["A database shared by all users", "A per-visitor dictionary kept between reruns",
     "A CSV file", "A secret key"], "answer": 1, "why": "Each browser session gets its own state dictionary."},
    {"q": "How does a chatbot app remember earlier messages?", "options": ["The model remembers automatically",
     "The app stores the message list in session_state and sends it each time", "Cookies", "It doesn't"], "answer": 1,
     "why": "The model has no memory; the app resends the history."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L1-3", "level": 1, "skill": "Dev Tools & Deploy", "minutes": 35,
"title": "Git and GitHub: saving and sharing your code",
"objectives": ["Make commits with clear messages", "Push a project to GitHub", "Keep secrets out of GitHub with .gitignore"],
"learn": d("""
### Why Git?
Git takes **snapshots** of your project (commits). You can go back in time, see what changed, and share.
**GitHub** stores those snapshots online — and Streamlit Cloud deploys directly from GitHub.

### First push
```bash
git init
git add .
git commit -m "Add attendance checker with columns layout"
git branch -M main
git remote add origin https://github.com/YOUR-NAME/my-first-app.git
git push -u origin main
```
### Every day after
```bash
git add .
git commit -m "Show classes needed to reach 75%"
git push
```
### .gitignore — files Git must NEVER upload
```
.venv/
.streamlit/secrets.toml
__pycache__/
```
⚠️ If an API key ever reaches GitHub, **delete that key on the provider's website immediately** and make a new one.

### Good commit messages
❌ `update`, `fixed stuff`  ✅ `Add CSV download to quiz generator`
"""),
"think": ["Why is a message like 'update' unhelpful when you look back after 3 months?",
          "If you accidentally pushed a key and then deleted the file, is the key safe? (Hint: snapshots…)"],
"practice": [
    {"kind": "build", "title": "Push your first project",
     "prompt": "Put your Attendance Checker on GitHub.",
     "checklist": ["Created a free GitHub account", "Created a .gitignore with .venv/ and .streamlit/secrets.toml",
                   "Made at least 2 commits with clear messages", "Pushed to a GitHub repository and can see the files online"],
     "hints": ["On GitHub: + → New repository → do NOT add a README (you already have files).",
               "Git may ask you to sign in: use the browser login window or a personal access token.",
               "Run `git status` any time you're unsure what Git sees."]},
],
"quiz": [
    {"q": "What is a commit?", "options": ["An upload to Streamlit", "A saved snapshot of your project with a message",
     "A Python error", "A branch"], "answer": 1, "why": "Commits are snapshots you can return to."},
    {"q": "Which file stops secrets.toml from being uploaded?", "options": ["requirements.txt", ".gitignore", "README.md", "Dockerfile"],
     "answer": 1, "why": ".gitignore lists files Git should ignore."},
    {"q": "You pushed an API key by mistake. Best action?", "options": ["Delete the file and push again",
     "Revoke/delete the key on the provider's site and create a new one", "Make the repo private later", "Nothing"],
     "answer": 1, "why": "Old snapshots still contain it — the key itself must be revoked."},
    {"q": "Which is the best commit message?", "options": ["changes", "fix", "Add CSV export to quiz page", "asdf"], "answer": 2,
     "why": "It says what changed and where."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L1-4", "level": 1, "skill": "Data", "minutes": 45,
"title": "Working with data: pandas basics",
"objectives": ["Load a table (DataFrame)", "Filter, sort and group data", "Show tables and charts in Streamlit"],
"learn": d("""
### pandas = Excel inside Python
```python
import pandas as pd
df = pd.read_csv("marks.csv")       # or pd.read_excel("marks.xlsx")
df.head()                           # first 5 rows
df.describe()                       # quick statistics
```
### The five moves you'll use 90% of the time
```python
df[df["marks"] >= 40]                         # FILTER rows
df.sort_values("marks", ascending=False)      # SORT
df["marks"].mean()                            # SUMMARISE a column
df.groupby("dept")["marks"].mean()            # GROUP: average per department
df["percent"] = df["marks"] / 150 * 100       # NEW column
```
### In Streamlit
```python
st.dataframe(df)
st.bar_chart(df.groupby("dept")["marks"].mean())
```
👉 Try it now in the **Data Lab** page with built-in sample datasets.
"""),
"think": ["What question about your own students could a groupby answer?",
          "Why might a mean (average) hide important information? What else would you look at?"],
"practice": [
    {"kind": "code", "title": "We do: average per department",
     "prompt": "Fill the blank so `avg_by_dept` holds the mean marks per department.",
     "starter": d("""
        import pandas as pd
        df = pd.DataFrame({
            "name":  ["Asha", "Ravi", "Meera", "John", "Sara", "Ali"],
            "dept":  ["Physics", "Commerce", "Physics", "Commerce", "Physics", "Commerce"],
            "marks": [82, 35, 67, 20, 91, 58],
        })
        avg_by_dept = df.groupby(___)["marks"].mean()
        print(avg_by_dept)
        """),
     "tests": d("""
        assert round(avg_by_dept["Physics"], 1) == 80.0, "Physics average should be 80.0"
        assert round(avg_by_dept["Commerce"], 1) == 37.7, "Commerce average should be 37.7"
        """),
     "hints": ["groupby needs the *name of the column* that defines the groups.", "It's a text: \"dept\".",
               "`df.groupby(\"dept\")[\"marks\"].mean()`"],
     "solution": d("""
        import pandas as pd
        df = pd.DataFrame({
            "name":  ["Asha", "Ravi", "Meera", "John", "Sara", "Ali"],
            "dept":  ["Physics", "Commerce", "Physics", "Commerce", "Physics", "Commerce"],
            "marks": [82, 35, 67, 20, 91, 58],
        })
        avg_by_dept = df.groupby("dept")["marks"].mean()
        """)},
    {"kind": "code", "title": "You do: toppers and pass rate",
     "prompt": "Using the same `df`, create:\n* `top3` – a list of the **names** of the 3 highest scorers, highest first\n"
               "* `pass_rate` – percentage of students with marks ≥ 40, rounded to 1 decimal",
     "starter": d("""
        import pandas as pd
        df = pd.DataFrame({
            "name":  ["Asha", "Ravi", "Meera", "John", "Sara", "Ali"],
            "dept":  ["Physics", "Commerce", "Physics", "Commerce", "Physics", "Commerce"],
            "marks": [82, 35, 67, 20, 91, 58],
        })
        # your code here
        """),
     "tests": d("""
        assert list(top3) == ["Sara", "Asha", "Meera"], f"top3 got {list(top3)}"
        assert pass_rate == 66.7, f"pass_rate should be 66.7, got {pass_rate}"
        """),
     "hints": ["Sort with `df.sort_values(\"marks\", ascending=False)` then `.head(3)`.",
               "Take the name column and turn it into a list: `[\"name\"].tolist()`.",
               "Passed count = `(df[\"marks\"] >= 40).sum()`; divide by `len(df)`, × 100, round."],
     "solution": d("""
        import pandas as pd
        df = pd.DataFrame({
            "name":  ["Asha", "Ravi", "Meera", "John", "Sara", "Ali"],
            "dept":  ["Physics", "Commerce", "Physics", "Commerce", "Physics", "Commerce"],
            "marks": [82, 35, 67, 20, 91, 58],
        })
        top3 = df.sort_values("marks", ascending=False).head(3)["name"].tolist()
        pass_rate = round((df["marks"] >= 40).sum() / len(df) * 100, 1)
        """)},
],
"quiz": [
    {"q": "What does `df[df[\"marks\"] >= 40]` return?", "options": ["True/False", "Only the rows where marks ≥ 40",
     "The marks column", "An error"], "answer": 1, "why": "A condition inside df[...] filters rows."},
    {"q": "Which gives the average per department?", "options": ["df.mean(\"dept\")", "df.groupby(\"dept\")[\"marks\"].mean()",
     "df.sort_values(\"dept\")", "df[\"dept\"].mean()"], "answer": 1, "why": "Group, pick column, summarise."},
    {"q": "What is a DataFrame?", "options": ["A chart", "A table of rows and columns in pandas", "A Streamlit widget", "A JSON file"],
     "answer": 1, "why": "It's pandas' table object."},
    {"q": "Which shows a table in Streamlit?", "options": ["st.table_show", "st.dataframe(df)", "print(df)", "st.csv(df)"],
     "answer": 1, "why": "st.dataframe gives an interactive table."},
],
},
# =============================================================================
# LEVEL 2
# =============================================================================
{
"id": "L2-1", "level": 2, "skill": "LLM Concepts", "minutes": 35,
"title": "How LLMs work: tokens, context, temperature",
"objectives": ["Explain tokens and why they matter for cost and limits", "Explain the context window",
               "Choose temperature for a task", "Compare model families and sizes"],
"learn": d("""
### Tokens
Models read **tokens** (pieces of words). Roughly **1 token ≈ ¾ of an English word**; Indian languages often use
more tokens per word. Limits and prices are counted in tokens.

### Context window
The maximum tokens the model can "see" at once — your prompt **plus** its answer **plus** chat history.
* ~128K tokens ≈ a 250-page book (many Groq models)
* ~1M tokens ≈ several textbooks (Gemini Flash)

### Temperature
| Temperature | Behaviour | Use for |
|---|---|---|
| 0 – 0.3 | Focused, repeatable | grading, JSON, facts, quizzes |
| 0.5 – 0.8 | Balanced | explanations, tutoring |
| 0.9 + | Creative, varied | brainstorming, stories |

### Model families you'll meet
| Family | Made by | Open weights? |
|---|---|---|
| GPT-OSS | OpenAI | ✅ (runs on Groq, OpenRouter, HF) |
| Llama | Meta | ✅ |
| Qwen | Alibaba | ✅ |
| Gemma / Gemini | Google | Gemma ✅ / Gemini ❌ |
| Mistral / Codestral | Mistral AI | some ✅ |

**Bigger** (e.g. 120B parameters) usually = smarter but slower; **smaller** (8B–20B) = faster and cheaper.
Models are **retired often** — always check the provider's live model list (the Model Lab does this for you).
"""),
"think": ["Why might a long PDF fail with one model but work with another?",
          "Which temperature would you choose for marking answer scripts — and why?"],
"practice": [
    {"kind": "reflect", "title": "Run a temperature experiment",
     "prompt": "Open **Model Lab → Playground**. Ask the same question 3 times at temperature 0, then 3 times at 1.2 "
               "(e.g. 'Give a creative title for a lecture on photosynthesis'). Describe what you observed and when "
               "you'd use each setting in teaching.",
     "rubric": ["Describes that low temperature gives similar/same answers", "Describes that high temperature varies more",
                "Gives a sensible teaching use for low temperature", "Gives a sensible use for high temperature"],
     "hints": ["Compare the 3 answers at temperature 0 — are they identical?", "What changed at 1.2?",
               "Think: grading vs brainstorming."]},
],
"quiz": [
    {"q": "Roughly how many English words is 1,000 tokens?", "options": ["100", "750", "5,000", "1 page of code"], "answer": 1,
     "why": "≈ ¾ word per token."},
    {"q": "Best temperature for generating answer keys?", "options": ["0–0.3", "0.8", "1.2", "2.0"], "answer": 0,
     "why": "Low temperature = consistent, focused output."},
    {"q": "The context window includes…", "options": ["Only your question", "Prompt + history + the answer",
     "Only the answer", "The model's training data"], "answer": 1, "why": "Everything the model processes in one request."},
    {"q": "Why does the app load a live model list?", "options": ["For decoration", "Models are retired and renamed often",
     "It's required by law", "To save tokens"], "answer": 1, "why": "Hard-coded model names break when models are retired."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L2-2", "level": 2, "skill": "Platforms & APIs", "minutes": 45,
"title": "Developer arenas: Groq, Google AI Studio, Mistral, OpenRouter, Hugging Face",
"objectives": ["Create free keys on at least two platforms", "Know what each platform is best for",
               "Use the playgrounds (no code) and then the Model Lab (code)"],
"learn": d("""
### The platforms (all have free tiers, no credit card)
| Platform | Get a key | Best for | Note |
|---|---|---|---|
| **Groq** | console.groq.com | Speed; open models (GPT-OSS, Qwen) | Playground in the console |
| **Google AI Studio** | aistudio.google.com | Gemini; huge context for PDFs; images | Excellent no-code prompt studio |
| **Mistral** | console.mistral.ai | Multilingual, Codestral for code | Free plan needs phone verification; may train on your data |
| **OpenRouter** | openrouter.ai | One key → hundreds of models; `:free` models | Small daily free limit |
| **Hugging Face** | huggingface.co | Datasets + open models; Spaces to host demos | Small monthly free credit |

### The secret that makes this easy
All of them speak the **same "OpenAI-compatible" language**. Only three things change:
```text
base_url   e.g. https://api.groq.com/openai/v1
api key    e.g. gsk_....
model      e.g. openai/gpt-oss-20b
```
So one function can talk to every provider — that's exactly how this app's Model Lab works.

### Workflow professionals use
1. **Explore** prompts in the platform's playground (no code).
2. **Copy** the settings into code.
3. **Compare** models side by side (Model Lab → Arena) before choosing one for your app.

⚠️ Free tiers have **rate limits** (requests per minute/day). For a class of 40, students can each use their own key.
⚠️ Never put student personal data into free tiers that may train on inputs.
"""),
"think": ["If you were building a tool that reads 200-page PhD theses, which platform would you try first, and why?",
          "What are the risks of sending student answer scripts to a free API?"],
"practice": [
    {"kind": "build", "title": "Open two developer arenas",
     "prompt": "Create free keys on **Groq** and **one other** platform. Paste them in **Profile & API Keys**, "
               "press **Test**, then send the same prompt to both in **Model Lab → Arena** and vote.",
     "checklist": ["Have a Groq key and it tests OK", "Have a second provider key and it tests OK",
                   "Tried a prompt in a platform's own playground (e.g. AI Studio)", "Compared two models in the Arena and voted"],
     "hints": ["Google AI Studio: sign in with Google → 'Get API key' → Create.",
               "OpenRouter: sign in → Keys → Create key; pick models ending with ':free'.",
               "If a test fails with 'model not found', press 'Load live model list' and choose one."]},
],
"quiz": [
    {"q": "What makes switching providers easy in code?", "options": ["They all use the same model",
     "Most offer an OpenAI-compatible API — change base_url, key and model", "They share one key", "Streamlit handles it"],
     "answer": 1, "why": "Same request shape everywhere."},
    {"q": "Which platform is especially known for very large context windows?", "options": ["Groq", "Google AI Studio (Gemini)",
     "GitHub", "Docker Hub"], "answer": 1, "why": "Gemini Flash models accept around 1M tokens."},
    {"q": "OpenRouter's main advantage?", "options": ["Fastest chips", "One key reaches many models from many labs",
     "Unlimited free use", "Hosts datasets"], "answer": 1, "why": "It routes to hundreds of models."},
    {"q": "A free API tier may use your inputs for training. So you should…", "options": ["Send everything anyway",
     "Avoid sending personal/sensitive student data", "Use temperature 0", "Use a bigger model"], "answer": 1,
     "why": "Protect student privacy; anonymise data."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L2-3", "level": 2, "skill": "Platforms & APIs", "minutes": 40,
"title": "Calling an LLM API from Python",
"objectives": ["Build a request (payload) as a dictionary", "Read the answer from the JSON response",
               "Handle errors and keep keys in st.secrets"],
"learn": d("""
### The request is just a dictionary
```python
import requests, streamlit as st

payload = {
    "model": "openai/gpt-oss-20b",
    "temperature": 0.2,
    "messages": [
        {"role": "system", "content": "You are a helpful tutor."},   # rules
        {"role": "user",   "content": "Explain osmosis in 2 lines."}, # question
    ],
}
r = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    json=payload,
    headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
)
data = r.json()
answer = data["choices"][0]["message"]["content"]
```
### The response is a nested dictionary
```json
{"choices": [{"message": {"role": "assistant", "content": "Osmosis is ..."}}],
 "usage": {"prompt_tokens": 25, "completion_tokens": 40}}
```
`data["choices"][0]["message"]["content"]` → go into `choices`, take item 0, then `message`, then `content`.

### Keys belong in `.streamlit/secrets.toml`
```toml
GROQ_API_KEY = "gsk_..."
```
and are read with `st.secrets["GROQ_API_KEY"]`.

### Errors you will meet
`401` wrong key · `404`/`model_not_found` retired model · `429` rate limit (wait and retry).
"""),
"think": ["Why is the system message separate from the user message?",
          "What would happen to your app if the provider returns an error and you still do data['choices'][0]?"],
"practice": [
    {"kind": "code", "title": "We do: build the payload",
     "prompt": "Complete `build_payload` so it returns the dictionary the API expects: keys `model`, `temperature` and "
               "`messages` (a system message, then a user message).",
     "starter": d("""
        def build_payload(model, system, question, temperature=0.2):
            return {
                "model": ___,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": ___},
                    {"role": ___, "content": question},
                ],
            }
        """),
     "tests": d("""
        p = build_payload("m1", "Be brief.", "What is DNA?")
        assert p["model"] == "m1"
        assert p["temperature"] == 0.2
        assert p["messages"][0] == {"role": "system", "content": "Be brief."}
        assert p["messages"][1] == {"role": "user", "content": "What is DNA?"}
        """),
     "hints": ["The model value comes from the `model` parameter.", "The system content is the `system` parameter.",
               "The second role is the text \"user\"."],
     "solution": d("""
        def build_payload(model, system, question, temperature=0.2):
            return {
                "model": model,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": question},
                ],
            }
        """)},
    {"kind": "code", "title": "You do: read the answer safely",
     "prompt": "Write `get_answer(data)` that returns the assistant's text from a response dictionary. "
               "If the response has an `\"error\"` key or no choices, return the text **\"ERROR\"** instead of crashing.",
     "starter": d("""
        def get_answer(data):
            # your code here
            return ""
        """),
     "tests": d("""
        ok = {"choices": [{"message": {"role": "assistant", "content": "Hello"}}]}
        assert get_answer(ok) == "Hello"
        assert get_answer({"error": {"message": "rate limit"}}) == "ERROR"
        assert get_answer({"choices": []}) == "ERROR"
        """),
     "hints": ["Check `if \"error\" in data` first.", "`data.get(\"choices\")` returns None if missing; an empty list is also 'falsy'.",
               "Then `return data[\"choices\"][0][\"message\"][\"content\"]`."],
     "solution": d("""
        def get_answer(data):
            if "error" in data or not data.get("choices"):
                return "ERROR"
            return data["choices"][0]["message"]["content"]
        """)},
],
"quiz": [
    {"q": "Where should the API key live in a Streamlit app?", "options": ["In app.py", "In .streamlit/secrets.toml / Cloud secrets",
     "In the README", "In the prompt"], "answer": 1, "why": "Secrets are kept out of code and GitHub."},
    {"q": "Error 429 usually means…", "options": ["Wrong key", "Too many requests — rate limit", "Model retired", "Success"],
     "answer": 1, "why": "Slow down or wait, then retry."},
    {"q": "Which path gets the answer text?", "options": ["data[\"answer\"]", "data[\"choices\"][0][\"message\"][\"content\"]",
     "data[\"message\"]", "data[0]"], "answer": 1, "why": "Follow the nesting of the JSON."},
    {"q": "The system message is for…", "options": ["The student's question", "Rules, role and style for the model",
     "Storing the key", "The answer"], "answer": 1, "why": "System = instructions that frame every answer."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L2-4", "level": 2, "skill": "Prompting", "minutes": 40,
"title": "Prompt engineering patterns",
"objectives": ["Write prompts with Role, Task, Context, Format", "Use few-shot examples", "Use Bloom's levels to control difficulty"],
"learn": d("""
### The R-T-C-F pattern
```text
Role:    You are an experienced physics professor.
Task:    Write 3 multiple-choice questions on Newton's laws.
Context: For first-year B.Sc. students; Bloom's level: Apply.
Format:  Numbered list. 4 options each. Mark the answer. One-line explanation.
```
Vague prompt → vague answer. Each line removes guesswork.

### Few-shot: show, don't just tell
Give 1–3 examples of the input → output you want, then the real input. The model copies the pattern.
```python
messages = [
  {"role": "system", "content": "Turn a topic into one exam question."},
  {"role": "user", "content": "Photosynthesis"},
  {"role": "assistant", "content": "Explain the role of chlorophyll in photosynthesis. (5 marks)"},
  {"role": "user", "content": "Inflation"},            # the real request
]
```

### Bloom's taxonomy as a difficulty dial
Remember → Understand → Apply → Analyse → Evaluate → Create. Naming the level in the prompt changes the questions dramatically.

### Other useful tricks
* "If you are not sure, say so." (reduces made-up answers)
* "Answer in under 100 words." (length control)
* "Think step by step, then give only the final answer." (better reasoning)
"""),
"think": ["Take a prompt you used recently. Which of Role, Task, Context, Format was missing?",
          "Why does showing an example often work better than describing what you want?"],
"practice": [
    {"kind": "code", "title": "We do: an R-T-C-F prompt builder",
     "prompt": "Complete `build_prompt(topic, level, n)` so the text contains the four labelled lines "
               "`Role:`, `Task:`, `Context:` and `Format:`, and mentions the topic, the Bloom's level and the number n.",
     "starter": d("""
        def build_prompt(topic, level, n):
            return (
                "Role: You are an experienced university teacher.\\n"
                f"Task: Write {___} multiple-choice questions on {___}.\\n"
                f"___: For undergraduate students. Bloom's level: {level}.\\n"
                "Format: ___"
            )
        """),
     "tests": d("""
        p = build_prompt("Inflation", "Apply", 5)
        for label in ["Role:", "Task:", "Context:", "Format:"]:
            assert label in p, f"missing {label}"
        assert "Inflation" in p and "Apply" in p and "5" in p, "topic, level and n must appear"
        assert "___" not in p, "fill every blank"
        """),
     "hints": ["Inside the f-string braces put the parameter names: `{n}` and `{topic}`.",
               "The third label is the word Context.", "Describe a format, e.g. 'Numbered list, 4 options, mark the answer.'"],
     "solution": d("""
        def build_prompt(topic, level, n):
            return (
                "Role: You are an experienced university teacher.\\n"
                f"Task: Write {n} multiple-choice questions on {topic}.\\n"
                f"Context: For undergraduate students. Bloom's level: {level}.\\n"
                "Format: Numbered list, 4 options each, mark the correct answer."
            )
        """)},
    {"kind": "code", "title": "You do: few-shot messages",
     "prompt": "Write `few_shot(system, examples, question)`. `examples` is a list of `(input, output)` pairs. "
               "Return the messages list: the system message, then for each pair a **user** message (input) followed by an "
               "**assistant** message (output), and finally the user's real `question`.",
     "starter": d("""
        def few_shot(system, examples, question):
            messages = [{"role": "system", "content": system}]
            # your code here
            return messages
        """),
     "tests": d("""
        m = few_shot("S", [("a", "A"), ("b", "B")], "c")
        assert [x["role"] for x in m] == ["system", "user", "assistant", "user", "assistant", "user"], [x["role"] for x in m]
        assert [x["content"] for x in m] == ["S", "a", "A", "b", "B", "c"]
        """),
     "hints": ["Loop: `for inp, out in examples:`", "Append two dictionaries per example: role user, then role assistant.",
               "After the loop, append `{\"role\": \"user\", \"content\": question}`."],
     "solution": d("""
        def few_shot(system, examples, question):
            messages = [{"role": "system", "content": system}]
            for inp, out in examples:
                messages.append({"role": "user", "content": inp})
                messages.append({"role": "assistant", "content": out})
            messages.append({"role": "user", "content": question})
            return messages
        """)},
    {"kind": "reflect", "title": "Improve a weak prompt",
     "prompt": "Rewrite this weak prompt using R-T-C-F for YOUR subject: **\"make questions on my topic\"**. "
               "Paste your improved prompt below.",
     "rubric": ["Has a clear Role", "Has a specific Task with number/type of questions", "Gives Context (students, level, Bloom's)",
                "Specifies an output Format"],
     "hints": ["Start with 'Role: You are…'", "Name the exact topic and how many questions.", "Say who the students are and the format."]},
],
"quiz": [
    {"q": "What does 'few-shot' mean?", "options": ["Using a small model", "Giving a few examples of input→output in the prompt",
     "Asking few questions", "Low temperature"], "answer": 1, "why": "Examples teach the pattern."},
    {"q": "Which part of R-T-C-F says 'Numbered list, 4 options'?", "options": ["Role", "Task", "Context", "Format"],
     "answer": 3, "why": "Format describes the shape of the output."},
    {"q": "To get higher-order thinking questions, mention…", "options": ["temperature 2", "Bloom's level: Analyse/Evaluate",
     "a bigger key", "more tokens"], "answer": 1, "why": "Bloom's levels steer cognitive demand."},
    {"q": "Which sentence reduces made-up answers?", "options": ["Be creative!", "If you are not sure, say so.",
     "Answer quickly.", "Use emojis."], "answer": 1, "why": "It gives the model permission to admit uncertainty."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L2-5", "level": 2, "skill": "Prompting", "minutes": 45,
"title": "Structured output: JSON mode and Pydantic",
"objectives": ["Ask a model for JSON", "Parse JSON into Python", "Validate data with Pydantic before showing it"],
"learn": d("""
### Why JSON?
Apps need **data**, not chatty paragraphs. "Sure! Here are your questions: …" breaks your code.
Ask for JSON and turn on JSON mode:
```python
payload["response_format"] = {"type": "json_object"}
```
### Parse it
```python
import json
quiz = json.loads(answer_text)          # text -> dictionary
quiz["questions"][0]["options"]
```
### Validate it with Pydantic (trust, but verify)
```python
from pydantic import BaseModel, field_validator

class MCQ(BaseModel):
    question: str
    options: list[str]
    answer: str

    @field_validator("options")
    @classmethod
    def four_options(cls, v):
        if len(v) != 4:
            raise ValueError("need exactly 4 options")
        return v

MCQ(**quiz["questions"][0])     # raises ValidationError if the model broke the rules
```
If validation fails → show a friendly message or ask the model again. Never let bad data crash your app.
"""),
"think": ["Why isn't 'please answer in JSON' in the prompt always enough?",
          "What could go wrong if the model's 'answer' isn't one of the options, and how would students be affected?"],
"practice": [
    {"kind": "code", "title": "We do: parse JSON text",
     "prompt": "`text` is what the model returned. Turn it into a dictionary and get the first question's answer.",
     "starter": d("""
        import json
        text = '{"questions": [{"question": "2+2?", "options": ["3","4","5","6"], "answer": "4"}]}'
        data = ___(text)
        first_answer = data["questions"][___]["answer"]
        """),
     "tests": "assert first_answer == '4', f'got {first_answer}'\nassert isinstance(data, dict)\n",
     "hints": ["The function that loads JSON from a string is in the json module.", "`json.loads(text)`",
               "The first item of a list has index 0."],
     "solution": d("""
        import json
        text = '{"questions": [{"question": "2+2?", "options": ["3","4","5","6"], "answer": "4"}]}'
        data = json.loads(text)
        first_answer = data["questions"][0]["answer"]
        """)},
    {"kind": "code", "title": "You do: validate with Pydantic",
     "prompt": "Create a Pydantic model `MCQ` (fields `question: str`, `options: list[str]`, `answer: str`) whose validation "
               "fails unless there are **exactly 4 options** and the **answer is one of the options**. Then write "
               "`is_valid(d)` returning True/False.",
     "starter": d("""
        from pydantic import BaseModel, ValidationError, model_validator

        class MCQ(BaseModel):
            question: str
            options: list[str]
            answer: str

            @model_validator(mode="after")
            def check(self):
                # raise ValueError(...) if something is wrong
                return self

        def is_valid(d):
            try:
                MCQ(**d)
                return True
            except ValidationError:
                return False
        """),
     "tests": d("""
        good = {"question": "Q", "options": ["a", "b", "c", "d"], "answer": "b"}
        assert is_valid(good), "a correct question should pass"
        assert not is_valid({**good, "options": ["a", "b", "c"]}), "3 options must fail"
        assert not is_valid({**good, "answer": "z"}), "answer not in options must fail"
        assert not is_valid({"question": "Q"}), "missing fields must fail"
        """),
     "hints": ["Inside `check`, use `self.options` and `self.answer`.", "`if len(self.options) != 4: raise ValueError(\"need 4\")`",
               "`if self.answer not in self.options: raise ValueError(\"answer must be an option\")`"],
     "solution": d("""
        from pydantic import BaseModel, ValidationError, model_validator

        class MCQ(BaseModel):
            question: str
            options: list[str]
            answer: str

            @model_validator(mode="after")
            def check(self):
                if len(self.options) != 4:
                    raise ValueError("need exactly 4 options")
                if self.answer not in self.options:
                    raise ValueError("answer must be one of the options")
                return self

        def is_valid(d):
            try:
                MCQ(**d)
                return True
            except ValidationError:
                return False
        """)},
],
"quiz": [
    {"q": "What does `json.loads` do?", "options": ["Downloads JSON", "Turns JSON text into Python data", "Saves a file", "Validates data"],
     "answer": 1, "why": "loads = load from string."},
    {"q": "Why validate with Pydantic?", "options": ["To make it faster", "To catch wrong/missing fields before they crash the UI",
     "Because JSON mode is illegal", "To save tokens"], "answer": 1, "why": "Models sometimes break the requested shape."},
    {"q": "JSON mode is enabled with…", "options": ["temperature=0", "response_format = {\"type\": \"json_object\"}",
     "max_tokens", "a system prompt only"], "answer": 1, "why": "It's a request parameter."},
    {"q": "If validation fails, a good app should…", "options": ["Crash", "Show a friendly message or retry",
     "Show raw JSON to students", "Delete the user"], "answer": 1, "why": "Graceful failure keeps learners' trust."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L2-6", "level": 2, "skill": "Data", "minutes": 40,
"title": "Datasets: finding, cleaning and using them",
"objectives": ["Know where to find good datasets", "Clean messy data (missing values, wrong types)",
               "Summarise data and ask an LLM about it responsibly"],
"learn": d("""
### Where to find datasets
| Source | What you'll find |
|---|---|
| **Hugging Face Datasets** (huggingface.co/datasets) | Text, Q&A, exam and language datasets for AI |
| **Kaggle** (kaggle.com/datasets) | Thousands of CSVs, with notebooks |
| **data.gov.in** | Indian government open data |
| **AISHE** (aishe.gov.in) | All India Survey on Higher Education statistics |
| **UCI ML Repository** | Classic small datasets, e.g. student performance |
| **Google Dataset Search** | A search engine for datasets |

Always check the **licence** and whether the data contains **personal information**.

### Cleaning: real data is messy
```python
df = df.dropna(subset=["marks"])                           # drop rows with missing marks
df["marks"] = pd.to_numeric(df["marks"], errors="coerce")  # "AB" (absent) -> NaN
df["dept"] = df["dept"].str.strip().str.title()            # " physics" -> "Physics"
```
### Data + LLM
Don't send a whole dataset to a model. Send a **summary** (`df.describe()`, column names, a few rows) and ask
for interpretation. The **Data Lab** page does exactly this.
"""),
"think": ["A marks file has 'AB' for absent students. What happens to the class average if you just delete those rows? Is that fair?",
          "What personal information should be removed before sharing a student dataset?"],
"practice": [
    {"kind": "code", "title": "We do: clean messy marks",
     "prompt": "The marks column contains 'AB' (absent). Convert it to numbers (AB → NaN), then drop rows with missing marks.",
     "starter": d("""
        import pandas as pd
        df = pd.DataFrame({"name": ["A", "B", "C", "D"], "marks": ["45", "AB", "78", "60"]})
        df["marks"] = pd.to_numeric(df["marks"], errors=___)
        clean = df.___(subset=["marks"])
        """),
     "tests": "assert len(clean) == 3, f'expected 3 rows, got {len(clean)}'\nassert clean['marks'].sum() == 183\n",
     "hints": ["errors=\"coerce\" turns things that aren't numbers into NaN.", "The method that drops missing values is dropna.",
               "`clean = df.dropna(subset=[\"marks\"])`"],
     "solution": d("""
        import pandas as pd
        df = pd.DataFrame({"name": ["A", "B", "C", "D"], "marks": ["45", "AB", "78", "60"]})
        df["marks"] = pd.to_numeric(df["marks"], errors="coerce")
        clean = df.dropna(subset=["marks"])
        """)},
    {"kind": "code", "title": "You do: attendance shortage report",
     "prompt": "Clean the `dept` column (strip spaces, Title Case), then build `shortage` – a dictionary "
               "`{dept: number of students with attendance < 75}` (include only departments with at least one).",
     "starter": d("""
        import pandas as pd
        df = pd.DataFrame({
            "dept": [" physics", "Physics", "commerce ", "Commerce", "History", "physics"],
            "attendance": [70, 90, 60, 74, 88, 50],
        })
        # your code here
        shortage = {}
        """),
     "tests": "assert shortage == {'Physics': 2, 'Commerce': 2}, f'got {shortage}'\n",
     "hints": ["`df[\"dept\"] = df[\"dept\"].str.strip().str.title()`", "Filter first: `low = df[df[\"attendance\"] < 75]`",
               "`low[\"dept\"].value_counts().to_dict()` gives the dictionary."],
     "solution": d("""
        import pandas as pd
        df = pd.DataFrame({
            "dept": [" physics", "Physics", "commerce ", "Commerce", "History", "physics"],
            "attendance": [70, 90, 60, 74, 88, 50],
        })
        df["dept"] = df["dept"].str.strip().str.title()
        low = df[df["attendance"] < 75]
        shortage = low["dept"].value_counts().to_dict()
        """)},
],
"quiz": [
    {"q": "Which site specialises in datasets for AI/NLP?", "options": ["Hugging Face Datasets", "YouTube", "Canva", "Docker Hub"],
     "answer": 0, "why": "HF hosts tens of thousands of ML datasets."},
    {"q": "`pd.to_numeric(..., errors='coerce')` turns 'AB' into…", "options": ["0", "NaN (missing)", "an error", "'AB'"],
     "answer": 1, "why": "coerce = convert what you can, mark the rest missing."},
    {"q": "Before sending data to an LLM you should…", "options": ["Send every row", "Send a summary and remove personal info",
     "Convert to PDF", "Use temperature 1"], "answer": 1, "why": "Privacy and context-window limits."},
    {"q": "What should you check before using a public dataset?", "options": ["Its colour", "Its licence and personal data",
     "The file name length", "Nothing"], "answer": 1, "why": "Legal and ethical use."},
],
},
# =============================================================================
# LEVEL 3
# =============================================================================
{
"id": "L3-1", "level": 3, "skill": "RAG & Apps", "minutes": 50,
"title": "RAG: answering from your own documents",
"objectives": ["Explain Retrieval-Augmented Generation", "Chunk text and retrieve relevant chunks",
               "Write a grounded prompt that refuses when the answer isn't there"],
"learn": d("""
### The problem
LLMs don't know your syllabus, your notes or last year's question paper — and may invent answers.

### RAG in three steps
1. **Chunk** – split documents into small pieces (e.g. 200 words).
2. **Retrieve** – find the chunks most related to the question.
3. **Generate** – send *only those chunks* plus the question, with the rule *"answer only from the context"*.

```python
chunks = chunk(pdf_text, size=200)
best = retrieve(chunks, question, k=3)
prompt = f"Answer ONLY from the context. If it isn't there, say 'Not in the document'.\\n\\n"
         f"Context:\\n{best}\\n\\nQuestion: {question}"
```
### Retrieval methods
* **Keyword overlap** – simple, no extra tools (we start here).
* **Embeddings** – turn text into vectors; finds meaning, not just words ("car" ≈ "automobile").
* **Big context shortcut** – with Gemini's ~1M tokens you can sometimes send the whole document — simpler but slower and costlier.

Try it in **App Gallery → PDF Study Assistant**.
"""),
"think": ["Why might keyword retrieval fail for the question 'How do plants make food?' when the notes say 'photosynthesis'?",
          "Why is 'say Not in the document' an important instruction for students?"],
"practice": [
    {"kind": "code", "title": "We do: chunk a document",
     "prompt": "Complete `chunk(text, size)` to split the text into pieces of `size` words (the last one can be shorter).",
     "starter": d("""
        def chunk(text, size):
            words = text.split()
            chunks = []
            for i in range(0, len(words), ___):
                chunks.append(" ".join(words[i:i + ___]))
            return chunks
        """),
     "tests": d("""
        assert chunk("a b c d e", 2) == ["a b", "c d", "e"]
        assert chunk("one two three", 5) == ["one two three"]
        assert chunk("", 3) == []
        """),
     "hints": ["We jump forward by the chunk size each time.", "Both blanks are the same parameter.", "`size`"],
     "solution": d("""
        def chunk(text, size):
            words = text.split()
            chunks = []
            for i in range(0, len(words), size):
                chunks.append(" ".join(words[i:i + size]))
            return chunks
        """)},
    {"kind": "code", "title": "You do: keyword retrieval",
     "prompt": "Write `retrieve(chunks, question, k=2)`. Score each chunk by how many times the question's words "
               "(lower-case, longer than 3 letters, with `?.,` stripped) appear in the lower-cased chunk. "
               "Return the top `k` chunks, best first (keep original order for ties).",
     "starter": d("""
        def retrieve(chunks, question, k=2):
            # your code here
            return chunks[:k]
        """),
     "tests": d("""
        docs = ["The cell membrane controls entry.", "Photosynthesis happens in chloroplasts using light.",
                "Mitochondria release energy. Energy powers the cell.", "Light energy is captured by chlorophyll."]
        assert retrieve(docs, "Where does photosynthesis happen?", k=1) == [docs[1]]
        assert retrieve(docs, "How is light energy captured?", k=2) == [docs[3], docs[2]]
        """),
     "hints": ["Make the word set: `{w.lower().strip('?.,') for w in question.split() if len(w) > 3}`",
               "Score: `sum(c.lower().count(w) for w in words)`", "`sorted(chunks, key=score, reverse=True)[:k]` – Python's sort is stable."],
     "solution": d("""
        def retrieve(chunks, question, k=2):
            words = {w.lower().strip("?.,") for w in question.split() if len(w) > 3}
            def score(c):
                return sum(c.lower().count(w) for w in words)
            return sorted(chunks, key=score, reverse=True)[:k]
        """)},
],
"quiz": [
    {"q": "What does the 'R' in RAG do?", "options": ["Randomises answers", "Retrieves relevant document pieces",
     "Repeats the question", "Rates the model"], "answer": 1, "why": "Retrieval finds the useful context."},
    {"q": "Why chunk documents?", "options": ["To make them prettier", "To send only relevant small pieces to the model",
     "To encrypt them", "It's required by Python"], "answer": 1, "why": "Smaller, focused context → better, cheaper answers."},
    {"q": "Embeddings help retrieval because…", "options": ["They are faster to type", "They match meaning, not just exact words",
     "They remove the need for a model", "They compress PDFs"], "answer": 1, "why": "Similar meanings have similar vectors."},
    {"q": "A good RAG prompt includes…", "options": ["'Use your imagination'", "'Answer only from the context; say if it's not there'",
     "'Ignore the context'", "Nothing special"], "answer": 1, "why": "This grounds answers and reduces hallucination."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L3-2", "level": 3, "skill": "RAG & Apps", "minutes": 45,
"title": "Chatbots with memory and personas (AI study twin)",
"objectives": ["Store chat history in session_state", "Design a persona with a system prompt",
               "Trim history to stay within the context window"],
"learn": d("""
### A chatbot = a loop of messages
```python
if "history" not in st.session_state:
    st.session_state.history = []

for m in st.session_state.history:                 # redraw old messages
    st.chat_message(m["role"]).write(m["content"])

if text := st.chat_input("Ask me…"):
    st.session_state.history.append({"role": "user", "content": text})
    reply = ask([{"role": "system", "content": PERSONA}] + st.session_state.history)
    st.session_state.history.append({"role": "assistant", "content": reply})
    st.rerun()
```
### Persona = the system prompt
```text
You are Mitra, a warm study companion for B.Ed students.
- Ask one question at a time. Never give full answers immediately (Socratic).
- Notice the student's mood; encourage effort, not just results.
- Keep replies under 100 words. End with one small next step.
- If a student seems distressed, respond kindly and suggest talking to a trusted person or counsellor.
```
### Memory limits
History grows every turn → eventually exceeds the context window and costs more.
Keep the **system prompt + the last N messages** (or summarise older ones).

The **Ask the Tutor** page in this app is built exactly this way.
"""),
"think": ["What should an AI study companion never do, even if a student asks?",
          "If you keep only the last 6 messages, what might the bot forget? How could a summary help?"],
"practice": [
    {"kind": "code", "title": "We do: add a message",
     "prompt": "Complete `add_message` so it appends a correctly shaped message and returns the history.",
     "starter": d("""
        def add_message(history, role, content):
            history.append({"role": ___, "content": ___})
            return history
        """),
     "tests": "h = add_message([], 'user', 'Hi')\nassert h == [{'role': 'user', 'content': 'Hi'}]\n",
     "hints": ["Use the parameters.", "role → role, content → content", "`{\"role\": role, \"content\": content}`"],
     "solution": d("""
        def add_message(history, role, content):
            history.append({"role": role, "content": content})
            return history
        """)},
    {"kind": "code", "title": "You do: trim the history",
     "prompt": "Write `trim_history(history, max_messages)`. If the first message is a system message, **always keep it**, "
               "plus the last `max_messages` non-system messages. Otherwise just keep the last `max_messages`.",
     "starter": d("""
        def trim_history(history, max_messages):
            # your code here
            return history
        """),
     "tests": d("""
        sys = {"role": "system", "content": "S"}
        msgs = [{"role": "user", "content": str(i)} for i in range(10)]
        out = trim_history([sys] + msgs, 3)
        assert out[0] == sys and [m["content"] for m in out[1:]] == ["7", "8", "9"], out
        out2 = trim_history(msgs, 2)
        assert [m["content"] for m in out2] == ["8", "9"], out2
        assert trim_history([sys], 3) == [sys]
        """),
     "hints": ["Check `history and history[0][\"role\"] == \"system\"`.", "The last n items of a list: `lst[-n:]`.",
               "`return [history[0]] + history[1:][-max_messages:]`"],
     "solution": d("""
        def trim_history(history, max_messages):
            if history and history[0]["role"] == "system":
                return [history[0]] + history[1:][-max_messages:]
            return history[-max_messages:]
        """)},
    {"kind": "reflect", "title": "Design your study twin's persona",
     "prompt": "Write a system prompt for an AI companion for YOUR students (name, personality, rules, safety). "
               "Then try it in **Ask the Tutor → Custom persona**.",
     "rubric": ["Gives a name and personality", "Sets teaching behaviour (e.g. Socratic, one question at a time)",
                "Controls length/format", "Includes a safety/wellbeing rule", "Fits a specific student group"],
     "hints": ["Start: 'You are …, a … for … students.'", "Add 3–5 bullet rules.", "Add one rule for distressed students."]},
],
"quiz": [
    {"q": "Where does a Streamlit chatbot keep the conversation?", "options": ["In the model", "In st.session_state",
     "In requirements.txt", "In GitHub"], "answer": 1, "why": "The app resends history from session_state each turn."},
    {"q": "Which defines the bot's personality?", "options": ["Temperature", "The system prompt", "The API key", "max_tokens"],
     "answer": 1, "why": "The system prompt sets role, tone and rules."},
    {"q": "Why trim chat history?", "options": ["To hide messages", "To stay within the context window and reduce cost",
     "Because Streamlit requires it", "To change the model"], "answer": 1, "why": "History grows every turn."},
    {"q": "A Socratic tutor mainly…", "options": ["Gives full answers immediately", "Asks guiding questions so students reason it out",
     "Refuses to help", "Only grades"], "answer": 1, "why": "Questions build understanding."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L3-3", "level": 3, "skill": "LLM Concepts", "minutes": 40,
"title": "Evaluating and comparing models",
"objectives": ["Build a small test set", "Measure accuracy and speed", "Choose a model with evidence, not hype"],
"learn": d("""
### Don't guess — test
Before you choose a model for an app, build a **mini benchmark**: 10–20 questions from your subject with known answers.

| Measure | How |
|---|---|
| **Accuracy** | correct answers ÷ total |
| **Speed (latency)** | seconds per answer |
| **Cost / limits** | tokens used, free-tier limits |
| **Quality** | blind side-by-side votes (the **Arena**) |
| **Safety & bias** | does it treat all student groups fairly? |

### Blind comparison
Show two answers labelled A and B without names; colleagues vote. Public leaderboards (like LMArena) use the same idea.

### Code idea
```python
results = {"model-x": [(True, 0.8), (False, 0.9)], "model-y": [(True, 2.1), (True, 1.9)]}
# (correct?, seconds) for each test question
```
Use **Model Lab → Arena** to compare models from different providers on your own questions.
"""),
"think": ["Model A is 95% accurate but takes 8 seconds; model B is 88% accurate and takes 1 second. Which would you use for a live classroom quiz, and for grading overnight?",
          "Why should you test with questions from *your* subject instead of trusting a public leaderboard?"],
"practice": [
    {"kind": "code", "title": "We do: accuracy",
     "prompt": "Complete `accuracy(preds, gold)` – the fraction of positions where the prediction equals the answer key, rounded to 2 decimals.",
     "starter": d("""
        def accuracy(preds, gold):
            correct = 0
            for p, g in zip(preds, gold):
                if ___:
                    correct += 1
            return round(correct / ___, 2)
        """),
     "tests": "assert accuracy(['a','b','c','d'], ['a','b','x','d']) == 0.75\nassert accuracy(['a'], ['b']) == 0.0\n",
     "hints": ["Compare p and g with ==.", "Divide by the number of questions.", "`len(gold)`"],
     "solution": d("""
        def accuracy(preds, gold):
            correct = 0
            for p, g in zip(preds, gold):
                if p == g:
                    correct += 1
            return round(correct / len(gold), 2)
        """)},
    {"kind": "code", "title": "You do: pick the best model",
     "prompt": "Write `best_model(results)`. `results` maps model name → list of `(correct: bool, seconds: float)`. "
               "Return the model with the **highest accuracy**; if tied, the one with the **lower average seconds**.",
     "starter": d("""
        def best_model(results):
            # your code here
            return ""
        """),
     "tests": d("""
        r = {"x": [(True, 1.0), (False, 1.0)], "y": [(True, 3.0), (True, 3.0)], "z": [(True, 1.0), (True, 1.0)]}
        assert best_model(r) == "z", best_model(r)
        assert best_model({"a": [(False, 1)], "b": [(True, 9)]}) == "b"
        """),
     "hints": ["For each model compute acc = sum(c for c, s in runs) / len(runs) and avg_s similarly.",
               "Use `max` with a key that returns a tuple: `(acc, -avg_s)`.",
               "`max(results, key=lambda m: (acc(m), -avg(m)))`"],
     "solution": d("""
        def best_model(results):
            def key(m):
                runs = results[m]
                acc = sum(c for c, s in runs) / len(runs)
                avg = sum(s for c, s in runs) / len(runs)
                return (acc, -avg)
            return max(results, key=key)
        """)},
],
"quiz": [
    {"q": "Accuracy = …", "options": ["tokens ÷ seconds", "correct ÷ total", "votes ÷ models", "temperature × 100"], "answer": 1,
     "why": "The share of questions answered correctly."},
    {"q": "Why compare models blindly (A vs B)?", "options": ["It's faster", "To avoid bias from brand names", "It's cheaper",
     "Models require it"], "answer": 1, "why": "Names influence judgement."},
    {"q": "For a live classroom tool, which matters a lot besides accuracy?", "options": ["Logo", "Latency (speed)", "Model's age", "Font"],
     "answer": 1, "why": "Students won't wait 10 seconds per answer."},
    {"q": "Why build your own test set?", "options": ["Leaderboards are illegal", "Your subject and students differ from general benchmarks",
     "It's required by Groq", "To use more tokens"], "answer": 1, "why": "Fitness for *your* use matters."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L3-4", "level": 3, "skill": "Dev Tools & Deploy", "minutes": 45,
"title": "Deploy: Streamlit Cloud, secrets and Docker",
"objectives": ["Deploy from GitHub to Streamlit Community Cloud", "Configure secrets online",
               "Understand Docker for other hosts", "Know the limits of free hosting"],
"learn": d("""
### Streamlit Community Cloud (free)
1. Push your project to GitHub (with `requirements.txt`).
2. Go to **share.streamlit.io** → sign in with GitHub → **Create app**.
3. Choose repo, branch `main`, main file `app.py`.
4. **Advanced settings → Secrets**:
```toml
GROQ_API_KEY = "gsk_..."
TEACHER_CODE = "choose-a-code"
```
5. **Deploy** → share the link.

### Free hosting limits
* Apps **sleep** after inactivity (first visitor waits ~30 s).
* The local file system is **temporary** — SQLite data resets on restart. For permanent data use a hosted
  database (Supabase, Google Sheets, Firebase) or download backups (this app's Teacher page does this).

### Docker — the portable box
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```
```bash
docker build -t my-app .
docker run -p 8501:8501 -e GROQ_API_KEY=gsk_... my-app
```
Docker images run the same on Hugging Face Spaces, Render, Railway, Google Cloud Run or a college server.
"""),
"think": ["Your class used the app all week, then the app restarted and progress vanished. What went wrong and how would you prevent it?",
          "When would a college prefer running the Docker image on its own server?"],
"practice": [
    {"kind": "build", "title": "Go live",
     "prompt": "Deploy an app (your Attendance Checker, a Gallery app, or this whole studio) to Streamlit Community Cloud.",
     "checklist": ["requirements.txt lists every package", "secrets.toml is NOT on GitHub",
                   "App deployed on share.streamlit.io", "Secrets added in Advanced settings", "Shared the link with at least 2 people"],
     "hints": ["If deployment fails, open 'Manage app' → logs: the last red line tells you the missing package.",
               "ModuleNotFoundError = add that package to requirements.txt and push.",
               "KeyError: 'GROQ_API_KEY' = secret missing or spelled differently."]},
],
"quiz": [
    {"q": "Where do secrets go on Streamlit Cloud?", "options": ["In app.py", "App settings → Secrets", "README", "requirements.txt"],
     "answer": 1, "why": "They're stored securely and read by st.secrets."},
    {"q": "Why might SQLite data vanish on Streamlit Cloud?", "options": ["SQLite is broken", "The container's file system resets on restart",
     "GitHub deletes it", "Secrets expire"], "answer": 1, "why": "Use an external database or backups."},
    {"q": "ModuleNotFoundError after deploying usually means…", "options": ["Wrong key", "A package is missing from requirements.txt",
     "Docker is required", "Too many users"], "answer": 1, "why": "The cloud only installs what's listed."},
    {"q": "Docker's main benefit?", "options": ["Free AI", "Same environment everywhere", "Faster models", "Automatic grading"],
     "answer": 1, "why": "The image bundles code + dependencies."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L3-5", "level": 3, "skill": "Responsible AI", "minutes": 35,
"title": "Responsible AI in higher education",
"objectives": ["Protect student privacy", "Recognise bias and hallucination risks", "Design for academic integrity and human oversight"],
"learn": d("""
### Five principles for AI tools in your institution
1. **Privacy** – anonymise (roll numbers, not names); avoid free tiers that train on inputs for sensitive data;
   follow India's **DPDP Act 2023** and your institution's policy.
2. **Accuracy** – AI-generated questions and feedback must be **reviewed by a teacher** before high-stakes use.
3. **Fairness** – test outputs across languages, genders, regions; watch for stereotyped examples.
4. **Transparency** – tell students when AI is used and how; cite sources (RAG helps).
5. **Integrity** – design tasks that reward process (drafts, viva, reflections), not just final text;
   AI detectors are unreliable — don't punish based on them alone.

### Human in the loop
AI drafts → teacher reviews → student receives. Especially for grades, feedback on wellbeing, and admissions.

### Student wellbeing
Companion bots must respond kindly to distress and point to real people (counsellor, helpline) — never replace them.
"""),
"think": ["A rubric-feedback app gives lower scores to answers written in Indian English. How would you detect and fix this?",
          "Which tasks in your course would you NEVER fully automate? Why?"],
"practice": [
    {"kind": "reflect", "title": "Write an AI-use policy for your class",
     "prompt": "Write a short AI-use policy (5–8 points) for your course: what students may/may not do with AI, "
               "how you'll use AI, and how data is protected.",
     "rubric": ["States allowed and not-allowed student uses", "Addresses privacy / data protection",
                "Includes teacher review / human oversight", "Addresses academic integrity fairly (not relying on detectors)",
                "Clear and student-friendly"],
     "hints": ["Split into 'Students may…', 'Students may not…', 'I will…'.", "Mention anonymised data.",
               "Add how students should acknowledge AI help."]},
],
"quiz": [
    {"q": "Best practice before using AI-generated exam questions?", "options": ["Use directly", "Teacher reviews and edits them",
     "Ask the AI if they're correct", "Use a higher temperature"], "answer": 1, "why": "Human review catches errors and bias."},
    {"q": "Which law governs personal data protection in India?", "options": ["IT Act 1950", "DPDP Act 2023", "RTE Act", "UGC Act 1956"],
     "answer": 1, "why": "The Digital Personal Data Protection Act, 2023."},
    {"q": "AI-text detectors are…", "options": ["Perfectly accurate", "Unreliable; shouldn't be sole evidence of misconduct",
     "Required by UGC", "Illegal"], "answer": 1, "why": "They produce false positives, especially for non-native writers."},
    {"q": "A companion bot detects a student in distress. It should…", "options": ["Ignore it", "Respond kindly and point to real human support",
     "Diagnose them", "Inform classmates"], "answer": 1, "why": "Bots support, humans care."},
],
},
# -----------------------------------------------------------------------------
{
"id": "L3-6", "level": 3, "skill": "RAG & Apps", "minutes": 120,
"title": "Capstone: build your own higher-education app",
"objectives": ["Plan an app around a real teaching problem", "Combine Streamlit, an LLM, JSON and data",
               "Deploy and gather feedback"],
"learn": d("""
### Pick a real problem
| Idea | Uses |
|---|---|
| Question bank generator by unit & Bloom's level | Prompting, JSON, CSV download |
| Rubric-based feedback assistant for assignments | Prompting, validation, human review |
| Syllabus / PDF study assistant | RAG |
| Attendance & marks early-warning dashboard | pandas, charts (no AI needed!) |
| Viva practice bot (Socratic examiner) | Chat memory, persona |
| Research question & proposal refiner | Prompting (FINER criteria) |
| Lesson plan generator (NEP-aligned, outcome-based) | Prompting, templates |

Start from a **template in the App Gallery** (download the starter code).

### Plan in one page
1. **Users** – who uses it?  2. **Input** – what do they give?  3. **Output** – what do they get?
4. **Model** – which provider/model and why (test in the Arena!)  5. **Risks** – privacy, errors, and how you'll handle them.
"""),
"think": ["What is the smallest version of your app that would already save you time this week?",
          "How will you know whether your app actually helps students learn?"],
"practice": [
    {"kind": "reflect", "title": "Capstone plan",
     "prompt": "Write your one-page plan: users, input, output, model choice, risks, and how you'll measure success.",
     "rubric": ["Clear user and problem", "Concrete input and output", "Justified model/provider choice",
                "Identifies risks and mitigations", "Has a way to measure success"],
     "hints": ["One sentence each for users and problem.", "Describe one screen of the app.", "Name one number you'll track (time saved, scores…)."]},
    {"kind": "build", "title": "Build and ship it",
     "prompt": "Build the smallest working version, deploy it, and get feedback from 3 users.",
     "checklist": ["Downloaded a starter template from the App Gallery (or started fresh)", "App works locally with my API key in secrets",
                   "Output is validated / reviewed before use", "Deployed on Streamlit Cloud", "Collected feedback from 3 users and made one improvement"],
     "hints": ["Keep version 1 tiny — one input, one output.", "Ask the tutor to review your code by pasting it.",
               "Write down what users struggled with — that's your next commit."]},
],
"quiz": [
    {"q": "The best first version of an app is…", "options": ["Feature-complete", "The smallest version that solves one real problem",
     "Whatever the AI suggests", "Never deployed"], "answer": 1, "why": "Ship small, learn, improve."},
    {"q": "Which gallery idea needs NO LLM at all?", "options": ["PDF assistant", "Marks early-warning dashboard", "Viva bot", "Quiz generator"],
     "answer": 1, "why": "pandas + charts are enough — not every problem needs AI."},
    {"q": "How should you pick the model for your app?", "options": ["The most famous one", "Test candidates on your own tasks (Arena / test set)",
     "The biggest one", "Random"], "answer": 1, "why": "Evidence over hype."},
    {"q": "A good success measure for a feedback assistant is…", "options": ["Number of tokens", "Time saved and quality of feedback rated by teachers/students",
     "Model size", "Number of commits"], "answer": 1, "why": "Measure the outcome you care about."},
],
},
]

LESSON_BY_ID = {l["id"]: l for l in LESSONS}


def lessons_for_level(level):
    return [l for l in LESSONS if l["level"] == level]


def lessons_for_skill(skill):
    return [l for l in LESSONS if l["skill"] == skill]


def quiz_bank(skills=None, lesson_ids=None):
    """All quiz questions tagged with their skill and lesson (used by the Practice Gym)."""
    bank = []
    for l in LESSONS:
        if skills and l["skill"] not in skills:
            continue
        if lesson_ids is not None and l["id"] not in lesson_ids:
            continue
        for i, q in enumerate(l["quiz"]):
            bank.append({**q, "skill": l["skill"], "lesson": l["id"], "qid": f"{l['id']}-q{i}"})
    return bank


def code_exercises(skills=None):
    out = []
    for l in LESSONS:
        if skills and l["skill"] not in skills:
            continue
        for i, ex in enumerate(l["practice"]):
            if ex["kind"] == "code":
                out.append({**ex, "skill": l["skill"], "lesson": l["id"], "exid": f"{l['id']}-ex{i}"})
    return out


# =============================================================================
# Plain-language descriptions (shown before the content, so nothing feels cryptic)
# =============================================================================
COURSE_ABOUT = """
**What is this course?** A step-by-step course that teaches you — even if you have *never* written code — to build
small AI-powered web apps for teaching, learning and research: quiz generators, feedback assistants, PDF study helpers,
data dashboards and AI study companions.

**How it works**
1. **Classes** – 21 short lessons in 4 levels. Each lesson has: 📖 a plain explanation → 🛠️ practice (first guided, then on
   your own) → ✅ a short quiz. Score 60% in the quiz to complete a lesson.
2. **Tutor** – stuck? Click *"🤷 I don't know – explain step by step"* and the AI tutor explains from zero, in simple steps.
3. **Practice Gym** – extra practice, focused on the skills where you scored lowest.
4. **Dashboard** (this page) – shows your progress, strong areas, weak areas, and what to do next.
5. **Explore** – Model Lab (try different AI models), Data Lab (work with real-shaped data), App Gallery (ready-made tools).

**You need:** a computer with internet. An AI key (free Groq key) is needed only for the AI features.
"""

LEVEL_ABOUT = {
    0: "Start here if you have never coded. You'll learn what AI, language models and APIs are (no code), then the first "
       "Python basics — storing values, lists, loops, decisions and functions — and how to set up your computer.",
    1: "You'll make your first web app with Streamlit (text boxes, sliders, buttons), learn why apps 'forget' things and how "
       "to fix it, save your code to GitHub, and handle tables of data (like marks lists) with pandas.",
    2: "You'll learn how AI models work (tokens, temperature), get free keys from developer platforms (Groq, Google AI Studio, "
       "Mistral…), call a model from Python, write good prompts, get reliable structured answers, and use datasets.",
    3: "You'll build real apps: answer questions from your own PDFs (RAG), chatbots with memory, compare models fairly, put "
       "your app online for others, use AI responsibly, and finish with your own capstone app.",
}

ABOUT = {
    "L0-1": "A no-code introduction. You'll understand, in everyday language, what an AI language model is, what an 'API' "
            "and an 'API key' are, and what you will build in this course.",
    "L0-2": "Your very first Python. You'll learn to store information in 'variables' (like labelled boxes), work with text "
            "and numbers, do simple maths like percentages, and print a sentence with your values inside it.",
    "L0-3": "How to handle many values at once. You'll keep a list of marks, go through them one by one with a 'for loop', "
            "and make decisions like pass/fail with 'if / elif / else'.",
    "L0-4": "How to write your own reusable 'functions' (mini-machines: input → output) and use 'dictionaries' to store "
            "labelled information like name → marks. AI apps use dictionaries everywhere.",
    "L0-5": "Setting up your own computer: VS Code (where you write code), the terminal (where you type commands), a "
            "virtual environment (a separate cupboard of tools per project) and pip (installs tools).",
    "L1-1": "Turn Python into a web page. You'll build an Attendance Checker app with text boxes, number inputs and messages, "
            "and arrange it in columns, tabs and a sidebar.",
    "L1-2": "Why apps 'forget' values when you click a button, and how to make them remember using session_state. "
            "You'll build a counter and a to-do list — the same idea makes chatbots remember a conversation.",
    "L1-3": "How to save versions of your code with Git and put it online on GitHub, so you can share it and later publish "
            "your app. Also: how to keep secret keys out of GitHub.",
    "L1-4": "Working with tables of data (like an Excel sheet of marks) using pandas: filter rows, sort, find averages per "
            "department, and show tables and charts in your app.",
    "L2-1": "What happens inside an AI model, in plain words: tokens (word pieces), the context window (how much it can "
            "read at once), and temperature (how creative vs. consistent the answers are).",
    "L2-2": "A tour of the free 'developer arenas' — Groq, Google AI Studio, Mistral, OpenRouter, Hugging Face — where you get "
            "API keys and try models. You'll learn that one piece of code can talk to all of them.",
    "L2-3": "Sending a question to an AI model from your own Python code, reading its reply, and handling errors — step by "
            "step, with the key stored safely.",
    "L2-4": "How to write prompts that get good results: a simple Role–Task–Context–Format recipe, giving examples "
            "('few-shot'), and using Bloom's levels to control question difficulty.",
    "L2-5": "Getting answers your app can use reliably: asking the model for JSON (structured data, like a form), reading it "
            "in Python, and checking it with Pydantic before showing it to students.",
    "L2-6": "Where to find good datasets (Hugging Face, Kaggle, data.gov.in, AISHE…), how to clean messy data like 'AB' for "
            "absent, and how to safely ask an AI about your data.",
    "L3-1": "Make the AI answer from YOUR documents (syllabus, notes, past papers) instead of guessing. This is called RAG: "
            "split the document, find the relevant parts, then ask the model using only those parts.",
    "L3-2": "Build a chatbot that remembers the conversation and has a personality (a 'study twin'), and learn how to keep "
            "its memory within limits.",
    "L3-3": "How to choose the right AI model with evidence: make a small test set, measure accuracy and speed, and compare "
            "models side by side without bias.",
    "L3-4": "Put your app on the internet for free with Streamlit Community Cloud, keep keys safe with 'secrets', and "
            "learn what Docker is for other hosting options.",
    "L3-5": "Using AI responsibly in a college: student privacy (DPDP Act 2023), checking AI output, fairness, honesty "
            "with students, and academic integrity.",
    "L3-6": "Plan, build and publish your own app for a real teaching or research problem, using everything from the course.",
}

for _l in LESSONS:
    _l["about"] = ABOUT.get(_l["id"], "")

# =============================================================================
# Syntax helper: symbols and ready-made code patterns (copy with one click)
# =============================================================================
SYMBOLS = [
    ("( )", "()", "brackets: call a function — print(x)"),
    ("[ ]", "[]", "square brackets: lists and indexing — marks[0]"),
    ("{ }", "{}", "curly brackets: dictionaries, and f-string slots"),
    ('" "', '""', "quotes: text (string)"),
    (":", ":", "colon: ends if / for / def lines"),
    ("=", "=", "store a value: x = 5"),
    ("==", "==", "compare: is equal?"),
    ("!=", "!=", "compare: not equal?"),
    (">=", ">=", "greater than or equal"),
    ("<=", "<=", "less than or equal"),
    ("_", "_", "underscore: used in names like total_marks"),
    ("#", "#", "comment (Python ignores the rest of the line)"),
    ("4 spaces", "    ", "indentation inside if / for / def"),
    ("f\"\"", 'f"{}"', "f-string: text with a value inside"),
    ("\\n", "\\n", "new line inside text"),
    ("%", "%", "remainder: 7 % 2 → 1"),
]

PATTERNS = {
    "Python": [
        ("Store a value", 'name = "Asha"\nage = 21'),
        ("Print with values (f-string)", 'print(f"{name} is {age} years old")'),
        ("Round a number", "percent = round(total / 150 * 100, 1)"),
        ("Make a list", "marks = [45, 78, 62]"),
        ("Add to a list", "marks.append(90)"),
        ("Loop over a list", "for m in marks:\n    print(m)"),
        ("If / elif / else", 'if m >= 75:\n    print("A")\nelif m >= 50:\n    print("B")\nelse:\n    print("C")'),
        ("Count with a loop", "count = 0\nfor m in marks:\n    if m >= 40:\n        count = count + 1"),
        ("Define a function", "def percentage(obtained, maximum):\n    return round(obtained / maximum * 100, 1)"),
        ("Make a dictionary", 'student = {"name": "Asha", "marks": 82}'),
        ("Read from a dictionary", 'student["name"]'),
        ("Loop over a dictionary", "for name, mark in marks.items():\n    print(name, mark)"),
        ("Sum, max, length", "sum(marks)\nmax(marks)\nlen(marks)"),
        ("Sorted list", "sorted(names)"),
    ],
    "Streamlit": [
        ("Import Streamlit", "import streamlit as st"),
        ("Title and text", 'st.title("My App")\nst.write("Hello")'),
        ("Text box", 'name = st.text_input("Your name")'),
        ("Number box", 'n = st.number_input("Classes attended", 0, 100, 40)'),
        ("Button", 'if st.button("Go"):\n    st.write("Clicked!")'),
        ("Remember a value", 'if "count" not in st.session_state:\n    st.session_state.count = 0'),
        ("Check a key in a dictionary", 'if "count" not in state:\n    state["count"] = 0'),
        ("Two columns", "c1, c2 = st.columns(2)"),
    ],
    "Data": [
        ("Import pandas", "import pandas as pd"),
        ("Read a CSV", 'df = pd.read_csv("marks.csv")'),
        ("Filter rows", 'df[df["marks"] >= 40]'),
        ("Sort", 'df.sort_values("marks", ascending=False)'),
        ("Average per group", 'df.groupby("dept")["marks"].mean()'),
        ("Top 3 names as a list", 'df.sort_values("marks", ascending=False).head(3)["name"].tolist()'),
        ("Text → numbers ('AB' → empty)", 'df["marks"] = pd.to_numeric(df["marks"], errors="coerce")'),
        ("Drop empty rows", 'df = df.dropna(subset=["marks"])'),
        ("Clean text", 'df["dept"] = df["dept"].str.strip().str.title()'),
        ("Count values → dictionary", 'df["dept"].value_counts().to_dict()'),
    ],
    "AI & JSON": [
        ("A message", '{"role": "user", "content": question}'),
        ("Messages list", 'messages = [\n    {"role": "system", "content": "You are a tutor."},\n    {"role": "user", "content": question},\n]'),
        ("Read the reply", 'data["choices"][0]["message"]["content"]'),
        ("Check a key exists", 'if "error" in data:\n    return "ERROR"'),
        ("Text → dictionary (JSON)", "import json\ndata = json.loads(text)"),
        ("Last n items of a list", "history[-3:]"),
        ("Split text into words", "words = text.split()"),
        ("Join words", '" ".join(words)'),
        ("Raise an error", 'raise ValueError("need exactly 4 options")'),
        ("Sort by a score, best first", "sorted(chunks, key=score, reverse=True)[:k]"),
    ],
}

PATTERN_GROUPS_BY_SKILL = {
    "Python": ["Python"], "Streamlit": ["Streamlit", "Python"], "Data": ["Data", "Python"],
    "Platforms & APIs": ["AI & JSON", "Python"], "Prompting": ["AI & JSON", "Python"],
    "RAG & Apps": ["AI & JSON", "Python"], "LLM Concepts": ["AI & JSON", "Python"],
}


# =============================================================================
# Fill-in-the-blank helper: work out the correct value for each ___ from the solution
# =============================================================================
def blank_answers(ex):
    """Return a list of correct fills for each ___ in the starter, or None if they can't be matched."""
    import re
    if ex.get("kind") != "code" or "___" not in ex.get("starter", ""):
        return None
    sol_lines = [l.rstrip() for l in ex["solution"].strip().splitlines()]
    answers, pos = [], 0
    for line in ex["starter"].strip().splitlines():
        line = line.rstrip()
        n = line.count("___")
        if not n:                       # fixed line: move past its twin in the solution (if it has one)
            for j in range(pos, len(sol_lines)):
                if sol_lines[j] == line:
                    pos = j + 1
                    break
            continue
        pattern = "^" + "(.+?)".join(re.escape(p) for p in line.split("___")) + "$"
        for j in range(pos, len(sol_lines)):
            m = re.match(pattern, sol_lines[j])
            if m:
                answers.extend(m.groups())
                pos = j + 1
                break
        else:
            return None
    return answers if len(answers) == ex["starter"].count("___") else None
