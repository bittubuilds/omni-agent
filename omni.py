#!/usr/bin/env python3
"""
OMNI CLI - chat with the OMNI agent in your terminal.

Pick a free brain (any one):
  GROQ         console.groq.com        -> export GROQ_API_KEY=...   (easiest)
  OPENROUTER   openrouter.ai/keys     -> export OPENROUTER_API_KEY=...
  GEMINI       aistudio.google.com    -> export GEMINI_API_KEY=...

Install:  pip install openai requests ddgs
Run:      python omni.py
"""

import os
import sys

from omni_core import SYSTEM_PROMPT, PROVIDERS, pick_provider

provider = pick_provider()
if not provider:
    sys.exit(
        "No API key found. Set one of:\n"
        "  export GROQ_API_KEY=...       (console.groq.com - easiest)\n"
        "  export OPENROUTER_API_KEY=... (openrouter.ai/keys)\n"
        "  export GEMINI_API_KEY=...     (aistudio.google.com/apikey)"
    )

from omni_core import make_agent

model = os.environ.get("MODEL", provider["model"])
reply = make_agent(os.environ[provider["env"]], provider["base_url"], model)

print(f"OMNI is live on {provider['label']} ({model}).")
print("Ask it anything. Type 'exit' to quit.\n")
messages = [{"role": "system", "content": SYSTEM_PROMPT}]
while True:
    try:
        user_input = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if not user_input:
        continue
    if user_input.lower() in ("exit", "quit"):
        break
    messages.append({"role": "user", "content": user_input})
    try:
        answer = reply(messages)
        messages.append({"role": "assistant", "content": answer})
        print("\nOMNI:", answer, "\n")
    except Exception as e:
        print(f"\n[error] {e}\n")
