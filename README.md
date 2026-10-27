# OMNI - Free General-Purpose AI Agent

A lightweight AI agent you can run for Rs 0, built on Google Gemini's free API tier.

## What it can do
- **Search the web** (DuckDuckGo, no API key needed)
- **Remember** facts permanently across conversations (`memory.json`)
- **Recall** anything it has remembered
- **Write and run Python code** (and generate code in any language)
- **Make decisions** by chaining the tools above

## Setup (5 minutes)
1. Get a free API key: https://aistudio.google.com/apikey
2. `pip install google-genai requests`
3. `export GEMINI_API_KEY=your_key`  (Windows: `set GEMINI_API_KEY=your_key`)
4. `python omni.py`

## Run in the cloud free
Host this on Hugging Face Spaces or a Render free instance instead of your laptop/phone.

## Notes
- Free tier has daily request caps and may slow down at busy hours.
- Extend it by adding new tools (functions) in the TOOLS section of `omni.py`.

Built as a starting point toward a "do anything" agent. Add tools, make it yours.
