#!/usr/bin/env python3
"""
OMNI Web - the OMNI agent as a browser app (Gradio).

Runs on a free Hugging Face Space. You open a URL in any browser and chat.
Search, memory, and code tools run on the server, not on your device.

Requires: GEMINI_API_KEY set (as a Space secret on Hugging Face).
Get a free key at https://aistudio.google.com/apikey
"""

import json
import os
import re
import subprocess
import sys
from urllib.parse import unquote

import requests
from google import genai
import gradio as gr

API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=API_KEY) if API_KEY else None
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
    # Primary: ddgs library (handles DuckDuckGo reliably)
    try:
        from ddgs import DDGS
        hits = list(DDGS().text(query, max_results=6))
        out = []
        for h in hits:
            out.append(f"- {h.get('title', '')} ({h.get('href', '')})\n  {h.get('body', '')}")
        if out:
            return "\n".join(out)
    except Exception:
        pass
    # Fallback: DuckDuckGo HTML directly
    try:
        r = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        import re
        results = []
        for m in re.finditer(
            r'<a[^>]+class="result__a"[^>]*href="[^"]*uddg=([^"]+)"[^>]*>(.*?)</a>', r.text
        ):
            from urllib.parse import unquote
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


# ---------------- CHAT ----------------

chat_session = None


def get_chat():
    global chat_session
    if chat_session is None and client is not None:
        chat_session = client.chats.create(
            model="gemini-2.0-flash",  # free tier
            config={
                "system_instruction": SYSTEM_PROMPT,
                "tools": [search_web, remember, recall, run_python],
            },
        )
    return chat_session


def respond(message, history):
    if client is None:
        return "Server is missing the GEMINI_API_KEY secret. Add it in the Space settings (Variables and secrets)."
    try:
        resp = get_chat().send_message(message)
        return resp.text
    except Exception as e:
        chat_reset = type("R", (), {"text": f"Error: {e}"})
        return f"Error: {e}"


demo = gr.ChatInterface(
    respond,
    title="OMNI - Free AI Agent",
    description="Searches the web, remembers facts, writes and runs code. Powered by Gemini free tier.",
)

if __name__ == "__main__":
    demo.launch()
