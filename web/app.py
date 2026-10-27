#!/usr/bin/env python3
"""
OMNI Web (Gradio) - for Hugging Face Spaces (requires HF PRO for Gradio hosting).

Set ONE secret in the Space settings:
  GROQ_API_KEY (easiest, console.groq.com) / OPENROUTER_API_KEY / GEMINI_API_KEY
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from omni_core import SYSTEM_PROMPT, PROVIDERS, pick_provider, make_agent

import gradio as gr

provider = pick_provider()
if not provider:
    raise RuntimeError(
        "Set one of the secrets GROQ_API_KEY / OPENROUTER_API_KEY / GEMINI_API_KEY"
    )

model = os.environ.get("MODEL", provider["model"])
reply = make_agent(os.environ[provider["env"]], provider["base_url"], model)
messages = [{"role": "system", "content": SYSTEM_PROMPT}]


def respond(message, history):
    messages.append({"role": "user", "content": message})
    try:
        answer = reply(messages)
        messages.append({"role": "assistant", "content": answer})
        return answer
    except Exception as e:
        return f"Error: {e}"


demo = gr.ChatInterface(
    respond,
    title="OMNI - Free AI Agent",
    description=f"Searches the web, remembers facts, writes and runs code. Brain: {provider['label']} ({model}).",
)

if __name__ == "__main__":
    demo.launch()
