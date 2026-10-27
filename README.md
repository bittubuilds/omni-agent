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

## Run OMNI in your browser (free, no install)

Streamlit Community Cloud hosts this agent free, straight from this repo:

1. Go to https://share.streamlit.io and sign in with GitHub (bittubuilds).
2. New app -> Repo: `omni-agent`, Branch: `main`, Main file path: `web/app_streamlit.py` -> Deploy.
3. In the app's Settings -> Secrets, add: `GEMINI_API_KEY = "your_free_key"`
   (free key: https://aistudio.google.com/apikey)
4. Open your permanent app URL in any browser and chat. Nothing installs on your device.

Note: free hosting has ephemeral storage (memory.json resets on restart) and
Hugging Face Spaces now requires a PRO subscription for Gradio apps, which is
why Streamlit Cloud is the free option.
