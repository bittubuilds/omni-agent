#!/usr/bin/env python3
"""
OMNI - a free, general-purpose AI agent you can run anywhere.

What it can do:
  - SEARCH the web (DuckDuckGo, no API key needed)
  - REMEMBER facts permanently (stored in memory.json)
  - RECALL anything it has remembered
  - WRITE AND RUN code in Python (any language logic can be generated too)
  - MAKE DECISIONS by chaining the tools above in a loop

Cost: Rs 0. Uses Google Gemini's free API tier.
Setup:
  1. Go to https://aistudio.google.com/apikey and create a free API key.
  2. pip install google-genai requests
  3. Set your key:  set GEMINI_API_KEY=your_key   (Windows)
                     export GEMINI_API_KEY=your_key  (Mac/Linux)
  4. Run:  python omni.py
"""

import json
import os
import subprocess
import sys
import textwrap

try:
    import requests
    from google import genai
except ImportError:
    sys.exit("Missing packages. Run:  pip install google-genai requests")

MEMORY_FILE = "memory.json"
API_KEY = os.environ.get("GEMINI_API_KEY", "")

if not API_KEY:
    sys.exit("Set your free Gemini API key first:\n  export GEMINI_API_KEY=your_key")

client = genai.Client(api_key=API_KEY)

SYSTEM_PROMPT = textwrap.dedent("""
    You are OMNI, a general-purpose AI agent. You help the user with ANY task.
    You have real tools. Use them actively:
    - When a question needs current facts, call search_web first.
    - When the user tells you something worth keeping (preferences, facts about
      them, ongoing projects), call remember.
    - When past context would help, call recall.
    - For calculations, data processing, or generating and testing code, call
      run_python. You can write code in any programming language as output.
    Think step by step and chain tools to accomplish complex tasks.
""")

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
    """Store a fact long-term so you can recall it in future conversations."""
    mem = _load_memory()
    mem.append({"fact": fact})
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)
    return "Remembered."


def recall(query: str) -> str:
    """Search your long-term memory for anything related to the query."""
    mem = _load_memory()
    q = query.lower()
    hits = [m["fact"] for m in mem if any(w in m["fact"].lower() for w in q.split())]
    if not hits:
        return "Nothing in memory about that."
    return "\n".join(f"- {h}" for h in hits)


def run_python(code: str) -> str:
    """Write and execute Python code (for math, data processing, file work, testing)."""
    try:
        p = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=30,
        )
        output = (p.stdout or "") + (p.stderr or "")
        return output[:4000] if output.strip() else "(ran successfully, no output)"
    except Exception as e:
        return f"Error: {e}"


# ---------------- MAIN LOOP ----------------

chat = client.chats.create(
    model="gemini-2.0-flash",  # free tier
    config={"system_instruction": SYSTEM_PROMPT,
            "tools": [search_web, remember, recall, run_python]},
)

print("OMNI is live. Ask it anything. Type 'exit' to quit.\n")
while True:
    try:
        user_input = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if not user_input:
        continue
    if user_input.lower() in ("exit", "quit"):
        break
    try:
        resp = chat.send_message(user_input)
        print("\nOMNI:", resp.text, "\n")
    except Exception as e:
        print(f"\n[error] {e}\n")
