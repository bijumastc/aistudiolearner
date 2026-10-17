"""Data Lab: explore built-in or uploaded datasets, clean them, chart them and ask an LLM about them."""
import pandas as pd
import streamlit as st

from core import auth, db, llm
from core.datasets import DATASETS, SOURCES

u = auth.current_user()
st.title("📈 Data Lab")
st.caption("Practise the pandas skills from lessons L1-4 and L2-6 on real-shaped data. Built-in data is synthetic (no real people).")

c1, c2 = st.columns([2, 1])
choice = c1.selectbox("Dataset", list(DATASETS) + ["📤 Upload my own CSV / Excel"])
if choice.startswith("📤"):
    up = c2.file_uploader("CSV or Excel", type=["csv", "xlsx"])
    if not up:
        st.info("Upload a file. ⚠️ Remove names, phone numbers and other personal data first.")
        st.stop()
    df = pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
    desc = f"Your file: {up.name}"
else:
    fn, desc = DATASETS[choice]
    df = fn()
c2.caption(desc)

t_view, t_explore, t_clean, t_ai, t_src = st.tabs(["👀 View", "🔎 Explore & chart", "🧹 Clean", "🤖 Ask AI", "🌐 Find datasets"])

with t_view:
    m1, m2, m3 = st.columns(3)
    m1.metric("Rows", len(df))
    m2.metric("Columns", df.shape[1])
    m3.metric("Missing cells", int(df.isna().sum().sum()))
    show = df.astype({c: str for c in df.columns if df[c].dtype == object})   # mixed text/number columns
    st.dataframe(show, width="stretch", height=380)
    st.download_button("⬇️ Download CSV", df.to_csv(index=False), "dataset.csv", "text/csv")
    st.code("df.head()\ndf.shape\ndf.isna().sum()", language="python")

with t_explore:
    num_cols = df.select_dtypes("number").columns.tolist()
    cat_cols = [c for c in df.columns if c not in num_cols and df[c].nunique() <= 30]
    st.markdown("**Summary statistics** — `df.describe()`")
    st.dataframe(df.describe().T.round(2), width="stretch")
    if num_cols:
        st.markdown("**Filter → Group → Chart**")
        f1, f2, f3 = st.columns(3)
        fcol = f1.selectbox("Filter column (optional)", ["—"] + cat_cols)
        sub = df
        if fcol != "—":
            vals = f2.multiselect("Keep values", sorted(df[fcol].dropna().astype(str).unique()))
            if vals:
                sub = df[df[fcol].astype(str).isin(vals)]
        g1, g2, g3 = st.columns(3)
        group = g1.selectbox("Group by", cat_cols or ["—"])
        metric = g2.selectbox("Measure", num_cols)
        agg = g3.selectbox("Statistic", ["mean", "median", "count", "sum", "min", "max"])
        if group != "—":
            res = sub.groupby(group)[metric].agg(agg).round(2).sort_values(ascending=False)
            st.bar_chart(res)
            st.code(f"df.groupby({group!r})[{metric!r}].{agg}()", language="python")
        if len(num_cols) >= 2:
            st.markdown("**Relationship between two numbers**")
            s1, s2 = st.columns(2)
            x = s1.selectbox("X", num_cols, index=0)
            y = s2.selectbox("Y", num_cols, index=min(1, len(num_cols) - 1))
            st.scatter_chart(sub, x=x, y=y)
            st.caption(f"Correlation: **{sub[x].corr(sub[y]):.2f}** (−1 to +1). Correlation is not causation!")

with t_clean:
    st.markdown("**Missing values per column**")
    miss = df.isna().sum()
    st.dataframe(miss[miss > 0].rename("missing").to_frame() if miss.any() else pd.DataFrame({"missing": []}),
                 width="stretch")
    obj_cols = [c for c in df.columns if df[c].dtype == object]
    numeric_like = [c for c in obj_cols if pd.to_numeric(df[c], errors="coerce").notna().mean() > 0.8]
    if numeric_like:
        st.warning(f"These columns look numeric but contain text (e.g. 'AB'): **{', '.join(numeric_like)}**")
        col = st.selectbox("Convert to numbers", numeric_like)
        clean = df.copy()
        clean[col] = pd.to_numeric(clean[col], errors="coerce")
        st.code(f'df[{col!r}] = pd.to_numeric(df[{col!r}], errors="coerce")', language="python")
        st.write(f"Mean of `{col}` after conversion: **{clean[col].mean():.2f}** "
                 f"({clean[col].isna().sum()} values became NaN)")
        how = st.radio("Then what about the missing values?", ["Leave them", "Drop those rows", "Fill with the median"], horizontal=True)
        if how == "Drop those rows":
            clean = clean.dropna(subset=[col])
            st.code(f"df = df.dropna(subset=[{col!r}])")
        elif how == "Fill with the median":
            clean[col] = clean[col].fillna(clean[col].median())
            st.code(f"df[{col!r}] = df[{col!r}].fillna(df[{col!r}].median())")
        st.caption(f"Rows now: {len(clean)}. 🤔 Which choice is fairest for absent students' class average?")
    else:
        st.success("No text-in-number columns detected.")

with t_ai:
    st.markdown("We send the model a **summary** (columns, statistics, a few rows) — never the whole file. "
                "This protects privacy and fits the context window.")
    q = st.text_area("Your question about this data",
                     "What are the 3 most important patterns here, and what should a teacher do about them?")
    if st.button("Ask", type="primary"):
        text_cols = [c for c in df.columns if df[c].dtype == object and df[c].astype(str).str.len().mean() > 25]
        context = (f"Columns and types:\n{df.dtypes.to_string()}\n\nSummary statistics:\n{df.describe(include='all').T.to_string()[:3500]}"
                   f"\n\nFirst 8 rows:\n{df.head(8).to_string()[:2500]}")
        if text_cols:
            context += f"\n\nSample of text column '{text_cols[0]}':\n" + "\n".join(df[text_cols[0]].astype(str).sample(min(25, len(df)), random_state=1))
        ans = llm.ask([
            {"role": "system", "content": "You are a careful education data analyst. Base claims only on the data summary given; "
                                          "say when something can't be concluded. Suggest one pandas line to verify each claim."},
            {"role": "user", "content": f"{context}\n\nQuestion: {q}"},
        ], temperature=0.2, max_tokens=2000)
        if ans:
            st.markdown(ans)
            db.log_event(u["username"], "data_lab", "ask ai")
        with st.expander("What the model saw"):
            st.text(context)

with t_src:
    st.markdown("Where to find real datasets — **always check the licence and remove personal data.**")
    for name, url, what in SOURCES:
        st.markdown(f"- **[{name}]({url})** — {what}")
    st.code("""import pandas as pd
df = pd.read_csv("https://.../file.csv")     # many open datasets load straight from a URL

# Hugging Face datasets (pip install datasets)
from datasets import load_dataset
ds = load_dataset("imdb", split="train[:1%]")
df = ds.to_pandas()""", language="python")
