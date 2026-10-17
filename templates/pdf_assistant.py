"""PDF study assistant (RAG) — starter template.
Run: streamlit run pdf_assistant.py
Ideas: multiple PDFs, embeddings for smarter retrieval, auto-generate a quiz from the PDF.
"""
import requests
import streamlit as st
from pypdf import PdfReader

st.set_page_config(page_title="PDF Study Assistant", page_icon="📄")

# ---- AI helper: works with Groq, Gemini, Mistral, OpenRouter, Hugging Face (change BASE_URL + MODEL) ----
BASE_URL = "https://api.groq.com/openai/v1"
MODEL = st.secrets.get("MODEL", "openai/gpt-oss-20b")      # check console.groq.com/docs/models for current names


def ask(messages, temperature=0.3, json_mode=False):
    payload = {"model": MODEL, "messages": messages, "temperature": temperature, "max_tokens": 3000}
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    r = requests.post(f"{BASE_URL}/chat/completions", json=payload, timeout=90,
                      headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"})
    if r.status_code != 200:
        st.error(f"API error {r.status_code}: {r.text[:300]}")
        st.stop()
    return r.json()["choices"][0]["message"]["content"]

st.title("📄 PDF Study Assistant")
up = st.file_uploader("Upload a PDF", type="pdf")
if not up:
    st.stop()

text = " ".join(page.extract_text() or "" for page in PdfReader(up).pages)
words = text.split()
chunks = [" ".join(words[i:i + 200]) for i in range(0, len(words), 200)]      # 1. CHUNK
st.caption(f"{len(chunks)} chunks")

q = st.text_input("Ask a question about the document")
if q:
    qwords = {w.lower().strip("?.,") for w in q.split() if len(w) > 3}
    best = sorted(chunks, key=lambda c: sum(c.lower().count(w) for w in qwords), reverse=True)[:4]   # 2. RETRIEVE
    context = "\n---\n".join(best)
    answer = ask([                                                                                   # 3. GENERATE
        {"role": "system", "content": "Answer ONLY from the context. If it is not there, say 'Not in the document.'"},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {q}"},
    ], temperature=0.1)
    st.markdown(answer)
    with st.expander("Passages used"):
        st.write(context)
