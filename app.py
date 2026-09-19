import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Secret retrieval (Streamlit Cloud or Local .env)
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="Guru - JEE/NEET AI Tutor", page_icon="📚")
st.title("⚡ Guru: JEE / NEET AI Buddy")
st.caption("Concept → Intuition → Formula → PYQ")

if not api_key:
    st.error("API Key missing! Please configure GEMINI_API_KEY in Secrets or .env file.")
    st.stop()

client = genai.Client(api_key=api_key)

SYSTEM_INSTRUCTION = """
You are 'Guru', a friendly, enthusiastic, best-friend style AI tutor for Indian students preparing for JEE and NEET.
Tone: Warm, conversational, encouraging Tanglish (Tamil + English blend). Like an elder brother or smart study buddy.

Core Teaching Flow for every new concept:
1. Concept Name: Direct and clear.
2. Intuition / Analogy: Relatable real-world example (cricket, daily life, cinema, mechanics).
3. Formula / Key Facts: Clear equations or core biology points.
4. 1 Previous Year Question (PYQ): Provide 1 standard exam MCQ with options (A, B, C, D) and challenge them to solve it.

CRITICAL RULE (Puriyala handling):
- If the user says 'puriyala', 'doubt', or seems confused, DO NOT repeat the same explanation.
- Switch to an entirely different analogy or mechanical/visual breakdown.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Doubt enna bro? Ask any topic (e.g. Lenz's Law, Glycolysis)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    contents = []
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

    with st.chat_message("assistant"):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            )
        )
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})