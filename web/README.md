---
title: OMNI Agent
emoji: 🤖
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
license: mit
short_description: Free general-purpose AI agent - search, memory, code
---

# OMNI Agent (Web)

A free general-purpose AI agent in your browser: web search, long-term memory,
and code execution, powered by Google Gemini's free tier.

## Setup on Hugging Face Spaces (free)
1. Create a Space with the Gradio SDK and upload these files.
2. In Settings -> Variables and secrets, add a secret:
   - Name: `GEMINI_API_KEY`
   - Value: your free key from https://aistudio.google.com/apikey
3. Open the Space URL in any browser and chat. Nothing installs on your device.

## Notes
- Keep the Space private so only you can use it (it can run code you send it).
- Free Spaces have ephemeral storage: memory.json resets if the Space restarts.
- Free tier has daily request caps and may slow down at busy hours.

Full CLI version and docs: https://github.com/bittubuilds/omni-agent
