#!/usr/bin/env python3
"""
OMNI Web (Streamlit) - browser AI agent, free hosting on Streamlit Community Cloud.

Deploy: https://share.streamlit.io -> sign in with GitHub ->
repo: bittubuilds/omni-agent | branch: main | file: web/app_streamlit.py

Set your free Gemini key once in the app's Settings -> Secrets:
    GEMINI_API_KEY = "your_key"
(or paste it in the sidebar each session).

Get a free key at https://aistudio.google.com/apikey
"""

import json
import os
import re
import subprocess
import sys
from urllib.parse import unquote

import requests
import streamlit as st
from google import genai

st.set_page_config(page_title="OMNI Agent", page_icon="🤖", layout="centered")

# ---- optional key from secrets / environment ----
try:
    DEFAULT_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    DEFAULT_KEY = os.environ.get("GEMINI_API_KEY", "")

MEMORY_FILE = "memory.json"

SYSTEM_PROMPT = (
    "You are OMNI, a general-purpose AI agent. You help the user with ANY task. "
    "You have real tools. Use them actively: "
    "- When a question needs current facts, call search_web first. "
    "- When the user tells you something worth keeping, call remember. "
    "- When past context would help, call recall. "
    "- For calculations, data processing, or code, call run_python. "
    "Think step by step and chain tools to accomplish complex tasks."
)


# ---------------- TOOLS ----------------

def search_web(query: str) -> str:
    """Search the internet (DuckDuckGo) and return the top results."""
    try:
        from ddgs import DDGS
        hits = list(DDGS().text(query, max_results=6))
        out = [f"- {h.get('title', '')} ({h.get('href', '')})\n  {h.get('body', '')}"
               for h in hits]
        if out:
            return "\n".join(out)
    except Exception:
        pass
    try:
        r = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        results = []
        for m in re.finditer(
            r'<a[^>]+class="result__a"[^>]*href="[^"]*uddg=([^"]+)"[^>]*>(.*?)</a>', r.text
        ):
            title = re.sub("<.*?>", "", m.group(2))
            results.append(f"- {title} ({unquote(m.group(1))})")
            if len(results) >= 6:
                break
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', r.text)[:6]
        out = []
        for i, res in enumerate(results):
            snip = re.sub("<.*?>", "", snippets[i]) if i < len(snippets) else ""
            out.append(f"{res}\n  {snip}")
        return "\n".join(out) if out else "No results found. Try different words."
    except Exception as e:
        return f"Search failed: {e}"


def _load_memory() -> list:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE) as f:
            return json.load(f)
    return []


def remember(fact: str) -> str:
    """Store a fact long-term so it can be recalled later."""
    mem = _load_memory()
    mem.append({"fact": fact})
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)
    return "Remembered."


def recall(query: str) -> str:
    """Search long-term memory for anything related to the query."""
    q = query.lower()
    hits = [m["fact"] for m in _load_memory()
            if any(w in m["fact"].lower() for w in q.split())]
    if not hits:
        return "Nothing in memory about that."
    return "\n".join(f"- {h}" for h in hits)


def run_python(code: str) -> str:
    """Write and execute Python code (math, data processing, testing)."""
    try:
        p = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=30,
        )
        output = (p.stdout or "") + (p.stderr or "")
        return output[:4000] if output.strip() else "(ran successfully, no output)"
    except Exception as e:
        return f"Error: {e}"


# ---------------- UI ----------------

st.title("OMNI - Free AI Agent")
st.caption("Searches the web · Remembers facts · Writes and runs code. Runs in the cloud, nothing installs on your device.")

with st.sidebar:
    st.header("Setup")
    key = st.text_input(
        "Gemini API key (free: aistudio.google.com/apikey)",
        type="password",
        value=DEFAULT_KEY,
    )
    if key and "chat" not in st.session_state:
        client = genai.Client(api_key=key)
        st.session_state.chat = client.chats.create(
            model="gemini-2.0-flash",  # free tier
            config={
                "system_instruction": SYSTEM_PROMPT,
                "tools": [search_web, remember, recall, run_python],
            },
        )
        st.success("Connected to Gemini.")
    if not key:
        st.info("Paste your free Gemini API key to start chatting.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Ask OMNI anything...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    if "chat" not in st.session_state:
        st.error("Paste your Gemini API key in the sidebar first.")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    resp = st.session_state.chat.send_message(prompt)
                    st.write(resp.text)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": resp.text}
                    )
                except Exception as e:
                    st.error(f"Error: {e}")
