"""
omni_core - shared engine for OMNI agent frontends (CLI, web, mobile).

Free brains (pick any, set the env var / pass the key):
  GROQ_API_KEY         -> console.groq.com        (easiest, generous free tier)
  OPENROUTER_API_KEY   -> openrouter.ai/keys      (models tagged :free)
  GEMINI_API_KEY       -> aistudio.google.com/apikey

All three speak the OpenAI-compatible API, so one engine drives them all.
"""

import json
import os
import re
import subprocess
import sys
from urllib.parse import unquote

import requests
from openai import OpenAI

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

MEMORY_FILE = os.environ.get("OMNI_MEMORY_FILE", "memory.json")
MAX_TOOL_ROUNDS = 8

SYSTEM_PROMPT = (
    "You are OMNI, a general-purpose AI agent. You help the user with ANY task. "
    "You have real tools. Use them actively: "
    "- When a question needs current facts, call search_web first. "
    "- When the user tells you something worth keeping (preferences, facts about "
    "them, ongoing projects), call remember. "
    "- When past context would help, call recall. "
    "- For calculations, data processing, or generating and testing code, call "
    "run_python. You can write code in any programming language as output. "
    "Think step by step and chain tools to accomplish complex tasks."
)

PROVIDERS = [
    {
        "env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.3-70b-versatile",
        "label": "Groq",
    },
    {
        "env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "label": "OpenRouter (free model)",
    },
    {
        "env": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-2.0-flash",
        "label": "Gemini",
    },
]


def pick_provider():
    """Return the first provider whose key is in the environment, or None."""
    return next((p for p in PROVIDERS if os.environ.get(p["env"])), None)


# ---------------- TOOLS ----------------

def search_web(query: str) -> str:
    """Search the internet (DuckDuckGo) and return the top results."""
    if DDGS is not None:
        try:
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
        try:
            with open(MEMORY_FILE) as f:
                return json.load(f)
        except Exception:
            return []
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


TOOL_IMPLS = {
    "search_web": search_web,
    "remember": remember,
    "recall": recall,
    "run_python": run_python,
}

TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "search_web",
        "description": "Search the internet for current information. Returns top results with titles, links, and snippets.",
        "parameters": {"type": "object",
                       "properties": {"query": {"type": "string", "description": "What to search for"}},
                       "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "remember",
        "description": "Store a fact long-term for recall in later conversations.",
        "parameters": {"type": "object",
                       "properties": {"fact": {"type": "string", "description": "The fact to store"}},
                       "required": ["fact"]}}},
    {"type": "function", "function": {
        "name": "recall",
        "description": "Search long-term memory for anything related to a query.",
        "parameters": {"type": "object",
                       "properties": {"query": {"type": "string", "description": "Topic to recall"}},
                       "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "run_python",
        "description": "Execute Python code for calculations, data processing, or testing. Returns stdout/stderr.",
        "parameters": {"type": "object",
                       "properties": {"code": {"type": "string", "description": "Python code to run"}},
                       "required": ["code"]}}},
]


def make_agent(api_key: str, base_url: str, model: str):
    """Return reply(messages)->str that runs the full tool-calling loop."""
    client = OpenAI(api_key=api_key, base_url=base_url)

    def reply(messages: list) -> str:
        for _ in range(MAX_TOOL_ROUNDS):
            resp = client.chat.completions.create(
                model=model, messages=messages, tools=TOOL_SCHEMAS,
            )
            msg = resp.choices[0].message
            if not msg.tool_calls:
                return msg.content or "(no response)"
            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name,
                                  "arguments": tc.function.arguments}}
                    for tc in msg.tool_calls
                ],
            })
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                fn = TOOL_IMPLS.get(tc.function.name)
                result = fn(**args) if fn else f"Unknown tool: {tc.function.name}"
                messages.append({"role": "tool", "tool_call_id": tc.id,
                                "content": str(result)})
        return "(hit tool limit, try asking more directly)"

    return reply
