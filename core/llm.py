"""
One helper for many AI providers.

Groq, Google AI Studio (Gemini), Mistral, OpenRouter and Hugging Face all offer an
"OpenAI-compatible" endpoint. That means the SAME request shape works everywhere —
only the base URL, the key and the model name change. This is the key idea of
the "Developer arenas" lesson.
"""
import hashlib
import json
import re
import time

import requests
import streamlit as st

PROVIDERS = {
    "Groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "secret": "GROQ_API_KEY",
        "models": ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3.8-27b"],
        "get_key": "https://console.groq.com/keys",
        "card": "No credit card",
        "about": "Extremely fast inference chips (LPUs). Hosts open models such as GPT-OSS and Qwen. "
                 "Great default for classroom apps.",
    },
    "Google AI Studio (Gemini)": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "secret": "GEMINI_API_KEY",
        "models": ["gemini-2.5-flash", "gemini-flash-latest", "gemma-3-27b-it"],
        "get_key": "https://aistudio.google.com/apikey",
        "card": "No credit card (Google account)",
        "about": "Google's Gemini models with very large context windows (great for long PDFs). "
                 "AI Studio also has a no-code prompt playground.",
    },
    "Mistral": {
        "base_url": "https://api.mistral.ai/v1",
        "secret": "MISTRAL_API_KEY",
        "models": ["mistral-small-latest", "mistral-large-latest", "ministral-8b-latest"],
        "get_key": "https://console.mistral.ai/api-keys",
        "card": "No credit card (phone verification; free 'Experiment' plan may use your data for training)",
        "about": "European lab with strong multilingual models and Codestral for code.",
    },
    "OpenRouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "secret": "OPENROUTER_API_KEY",
        "models": ["openai/gpt-oss-120b:free", "meta-llama/llama-3.3-70b-instruct:free", "qwen/qwen3-coder:free"],
        "get_key": "https://openrouter.ai/keys",
        "card": "No credit card (free models end in ':free'; small daily limit)",
        "about": "A single key that reaches hundreds of models from many labs. Perfect for comparing models.",
    },
    "Hugging Face": {
        "base_url": "https://router.huggingface.co/v1",
        "secret": "HF_TOKEN",
        "models": ["openai/gpt-oss-120b", "meta-llama/Llama-3.1-8B-Instruct", "Qwen/Qwen2.5-7B-Instruct"],
        "get_key": "https://huggingface.co/settings/tokens",
        "card": "No credit card (small monthly free credit)",
        "about": "The 'GitHub of AI': hosts models AND datasets. Its router sends your request to partner providers.",
    },
}


def _secret(name):
    try:
        return st.secrets.get(name, "")
    except Exception:
        return ""


def get_key(provider):
    """Key typed by the learner this session wins; otherwise use app secrets."""
    typed = st.session_state.get("api_keys", {}).get(provider, "")
    return typed or _secret(PROVIDERS[provider]["secret"])


def available_providers():
    return [p for p in PROVIDERS if get_key(p)]


def default_provider():
    avail = available_providers()
    preferred = st.session_state.get("default_provider")
    if preferred in avail:
        return preferred
    return avail[0] if avail else None


def default_model(provider):
    chosen = st.session_state.get("default_models", {}).get(provider)
    return chosen or PROVIDERS[provider]["models"][0]


@st.cache_data(ttl=3600, show_spinner=False)
def _list_models_cached(provider, key_fingerprint, key):
    base = PROVIDERS[provider]["base_url"]
    r = requests.get(f"{base}/models", headers={"Authorization": f"Bearer {key}"}, timeout=20)
    r.raise_for_status()
    ids = [m.get("id", "") for m in r.json().get("data", [])]
    ids = [i.replace("models/", "") for i in ids if i]
    return sorted(set(ids))


def list_models(provider):
    """Ask the provider which models exist RIGHT NOW (models get retired often!)."""
    key = get_key(provider)
    if not key:
        return []
    fp = hashlib.sha256(key.encode()).hexdigest()[:12]
    try:
        return _list_models_cached(provider, fp, key)
    except Exception:
        return []


def chat(messages, provider=None, model=None, temperature=0.4, max_tokens=1500, json_mode=False):
    """Send a chat request. Returns dict(text, latency, usage, error, provider, model)."""
    provider = provider or default_provider()
    out = {"text": None, "latency": 0.0, "usage": {}, "error": None, "provider": provider, "model": model}
    if not provider:
        out["error"] = "NO_KEY"
        return out
    key = get_key(provider)
    if not key:
        out["error"] = "NO_KEY"
        return out
    model = model or default_model(provider)
    out["model"] = model
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    if provider == "Groq" and "gpt-oss" in model:
        payload["reasoning_effort"] = "low"   # faster answers for classroom use
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    url = f"{PROVIDERS[provider]['base_url']}/chat/completions"
    t0 = time.time()
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=90)
        if r.status_code >= 400 and json_mode:      # some models don't support JSON mode -> retry without
            payload.pop("response_format", None)
            r = requests.post(url, headers=headers, json=payload, timeout=90)
        out["latency"] = time.time() - t0
        if r.status_code >= 400:
            try:
                msg = r.json().get("error", {})
                msg = msg.get("message", msg) if isinstance(msg, dict) else msg
            except Exception:
                msg = r.text[:300]
            out["error"] = f"{r.status_code}: {msg}"
            return out
        data = r.json()
        out["text"] = (data["choices"][0]["message"].get("content") or "").strip()
        out["usage"] = data.get("usage", {}) or {}
    except Exception as e:  # network problems etc.
        out["error"] = str(e)
    return out


def ask(messages, **kw):
    """Convenience wrapper used by pages: shows friendly errors, returns text or None."""
    res = chat(messages, **kw)
    if res["error"] == "NO_KEY":
        st.warning("🔑 This feature needs an AI key. Open **Profile & API Keys** and paste your free Groq key.")
        return None
    if res["error"]:
        st.error(f"The AI provider returned an error — {res['error']}")
        if "model" in str(res["error"]).lower():
            st.info("Tip: models get retired. Go to **Profile & API Keys** → load the live model list and pick another.")
        return None
    return res["text"]


def extract_json(text):
    """Models sometimes wrap JSON in ```fences``` or add a sentence. Pull out the JSON object."""
    if text is None:
        raise ValueError("empty response")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", text, re.S)
    if m:
        return json.loads(m.group(1))
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        return json.loads(text[start:end + 1])
    raise ValueError("No JSON found in the model's reply")


def python_snippet(provider, model, system, user, temperature):
    """Show learners the exact code behind what they just did."""
    base = PROVIDERS[provider]["base_url"]
    sec = PROVIDERS[provider]["secret"]
    return f'''import requests, streamlit as st

API_KEY = st.secrets["{sec}"]          # never paste keys into code!
URL = "{base}/chat/completions"

payload = {{
    "model": "{model}",
    "temperature": {temperature},
    "messages": [
        {{"role": "system", "content": {system!r}}},
        {{"role": "user", "content": {user!r}}},
    ],
}}
r = requests.post(URL, json=payload, headers={{"Authorization": f"Bearer {{API_KEY}}"}})
print(r.json()["choices"][0]["message"]["content"])
'''
