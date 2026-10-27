#!/usr/bin/env python3
"""
OMNI Web (Streamlit) - browser AI agent, free hosting on Streamlit Community Cloud.

Deploy: https://share.streamlit.io -> sign in with GitHub ->
repo: bittubuilds/omni-agent | branch: main | file: web/app_streamlit.py

Add your free key once in the app's Settings -> Secrets (any ONE):
    GROQ_API_KEY = "your_key"       <- easiest, console.groq.com
    OPENROUTER_API_KEY = "your_key" <- openrouter.ai/keys
    GEMINI_API_KEY = "your_key"     <- aistudio.google.com/apikey

Or just pick a provider in the sidebar and paste the key each session.
"""

import os
import sys

# allow importing omni_core from the repo root when running from web/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(page_title="OMNI Agent", page_icon="🤖", layout="centered")

from omni_core import SYSTEM_PROMPT, PROVIDERS, make_agent

st.title("OMNI - Free AI Agent")
st.caption("Searches the web · Remembers facts · Writes and runs code. Runs in the cloud, nothing installs on your device.")

# ---- read keys from secrets (set once in Streamlit app settings) ----
secret_keys = {}
for p in PROVIDERS:
    try:
        secret_keys[p["env"]] = st.secrets.get(p["env"], "")
    except Exception:
        secret_keys[p["env"]] = os.environ.get(p["env"], "")

with st.sidebar:
    st.header("Brain")
    available = [p["label"] for p in PROVIDERS if secret_keys.get(p["env"])]
    default_label = available[0] if available else PROVIDERS[0]["label"]
    choice = st.selectbox("Free AI provider", [p["label"] for p in PROVIDERS],
                          index=[p["label"] for p in PROVIDERS].index(default_label))
    provider = next(p for p in PROVIDERS if p["label"] == choice)
    key = secret_keys.get(provider["env"]) or st.text_input(
        f"API key (free from {provider['label']})", type="password"
    )

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

connected = False
if key:
    cache_id = (provider["env"], key, provider["model"])
    if st.session_state.get("agent_id") != cache_id:
        try:
            st.session_state.agent = make_agent(key, provider["base_url"], provider["model"])
            st.session_state.agent_id = cache_id
        except Exception as e:
            st.error(f"Failed to connect: {e}")
    connected = st.session_state.get("agent") is not None

if not connected:
    st.info(f"👆 Paste your free {provider['label']} API key in the sidebar to start. "
            f"Get one at {provider['label'].split()[0].lower()}: see repo README for links.")

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Ask OMNI anything...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    if not connected:
        st.error("Add your API key in the sidebar first.")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = st.session_state.agent(st.session_state.messages)
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Error: {e}")
