# OMNI - Free General-Purpose AI Agent

A lightweight AI agent that runs for Rs 0. Web search, long-term memory, code
execution, and tool-chaining decisions, powered by any free AI provider.

## Pick a free brain (any ONE, no credit card)

| Provider | Get a free key | Env var | Notes |
|---|---|---|---|
| **Groq** (easiest) | https://console.groq.com | `GROQ_API_KEY` | Fast, generous free tier, GPT-OSS-120B |
| **OpenRouter** | https://openrouter.ai/keys | `OPENROUTER_API_KEY` | Free models tagged `:free` |
| **Gemini** | https://aistudio.google.com/apikey | `GEMINI_API_KEY` | Google free tier |

All three are interchangeable - same agent, same tools.

## Run on your computer (CLI)

```
pip install -r requirements.txt
export GROQ_API_KEY=your_key        # Windows: set GROQ_API_KEY=your_key
python omni.py
```

## Run in your browser (free, no install)

Streamlit Community Cloud hosts this agent free, straight from this repo:

1. Go to https://share.streamlit.io and sign in with GitHub.
2. New app -> Repo: `omni-agent`, Branch: `main`, Main file path: `web/app_streamlit.py` -> Deploy.
3. In the app's Settings -> Secrets, add ONE of:
   `GROQ_API_KEY = "your_key"` (easiest) or `OPENROUTER_API_KEY = "..."` or `GEMINI_API_KEY = "..."`
4. Open your permanent app URL in any browser and chat. Nothing installs on your device.

## Hugging Face Space (optional)

`web/app.py` is a Gradio version for HF Spaces. Note: HF now requires a PRO
subscription to host Gradio apps, so Streamlit Cloud is the free option.

## What it can do

- **Search the web** (DuckDuckGo via `ddgs`, no API key needed)
- **Remember** facts permanently across conversations (`memory.json`)
- **Recall** anything it has remembered
- **Write and run Python code** (and generate code in any language)
- **Make decisions** by chaining the tools above (max 8 tool rounds per reply)

## Notes

- Free tiers have daily request caps and may slow down at busy hours.
- On free web hosting, storage is ephemeral: `memory.json` resets on app restart.
- Use the `MODEL` env var to switch models (e.g. a different `:free` OpenRouter model).
- Keep web deployments private - the agent runs code you send it.

## Structure

- `omni_core.py` - shared engine (tools + provider-agnostic chat loop)
- `omni.py` - CLI chat
- `web/app_streamlit.py` - Streamlit browser app (free hosting)
- `web/app.py` - Gradio browser app (HF Spaces)

Add tools by defining a function + schema in `omni_core.py` and registering it in
`TOOL_IMPLS` / `TOOL_SCHEMAS`. That's the path to a "do anything" agent.

## Browser edition (HF static Space) - deployed

`static/index.html` is a fully self-contained browser agent (no server needed):
chat + tool loop runs client-side on Groq's API, search via DuckDuckGo/Wikipedia
APIs, memory in localStorage, code execution in JavaScript. It powers the private
HF Space. The API key lives only in the Space, never in this repo.

## OMNI v2 (browser edition) features

- Live web search (DuckDuckGo + Wikipedia)
- Weather for any city (Open-Meteo, keyless)
- AI image generation (Pollinations, keyless)
- Long-term memory + memory manager (view/delete in menu)
- Runs JavaScript (calculations, data processing)
- Voice input (mic, Hindi/English) and voice replies
- Attach text/code/CSV/JSON files and ask about them
- Saved chat history (last 15 chats), markdown answers with copy buttons

## ULTRON UI (v2.1)

Command-center redesign: neon red on black, sidebar (Home/Task Manager/Memory/
Models/Tools/Settings/Logs), hero with pulsing halo, capability cards, live
system status (real API latency/network/localStorage metrics), task manager the
agent updates itself (add_task/complete_task tools), activity logs, model
switcher (live Groq model list). Fully responsive; on phones sidebar and status
panel become drawers.
