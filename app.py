import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

st.set_page_config(
    page_title="Guru - JEE/NEET AI Tutor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for Sleek Modern Look
st.markdown(
    """
    <style>
        .stApp {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        .main-title {
            font-size: 2.1rem;
            font-weight: 700;
            margin-bottom: 2px;
        }
        .sub-caption {
            color: #8b949e;
            font-size: 0.95rem;
            margin-bottom: 20px;
        }
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if not api_key:
    st.error("API Key missing! Check Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# ----------------- SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.title("⚙️ Tutor Settings")

    subject = st.selectbox(
        "Select Subject:",
        ["Physics", "Chemistry", "Biology", "Mathematics", "General JEE/NEET Guidance"],
    )

    mode = st.radio(
        "Teaching Mode:",
        [
            "Full Concept Flow (Analogy + Formula + PYQ)",
            "Rapid PYQ Drill (Direct Question)",
            "Formula / Concept Cheat Sheet",
        ],
    )

    st.divider()
    st.markdown("### 📸 Doubt Image Upload")
    uploaded_image = st.file_uploader(
        "Upload Question / Diagram photo:",
        type=["png", "jpg", "jpeg"],
        help="Take a clear photo of your question or textbook diagram",
    )

    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Doubt", use_container_width=True)

    st.divider()
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# ----------------- PROMPT INSTRUCTION -----------------
SYSTEM_INSTRUCTION = f"""
You are 'Guru', a top-tier mentor and best-friend style AI tutor for Indian students preparing for JEE and NEET.
Current Subject Focus: {subject}
Active Learning Mode: {mode}

Tone & Language:
- Friendly, encouraging, smart Tanglish (Tamil + English blend).
- Speak like a friendly study buddy or elder brother (using terms like 'bro', 'thala', 'kavanama paaru').

Rules based on Mode:
1. If mode is 'Full Concept Flow':
   - Concept Name
   - Relatable Intuition / Real-life Analogy
   - Key Formulae / Core Points
   - 1 Standard PYQ MCQ with 4 options (A, B, C, D)
2. If mode is 'Rapid PYQ Drill':
   - Directly present 1 tricky PYQ with options and ask the user to choose an answer before revealing the solution.
3. If mode is 'Formula / Concept Cheat Sheet':
   - Deliver high-yield formulas, short notes, and common traps/mistakes in a clean format.

Vision / Image Doubt Handling:
- If an image is provided, identify the specific question/diagram in it, solve it step-by-step in Tanglish, and highlight the core trick.

CRITICAL RULE (Puriyala handling):
- If the student says 'puriyala', 'doubt', or seems stuck, NEVER repeat the old explanation. Switch entirely to a simpler, visual, mechanical, or daily-life example.
"""

# ----------------- CHAT INTERFACE -----------------
st.markdown('<div class="main-title">⚡ Guru: JEE / NEET AI Buddy</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-caption">Current Subject: <b>{subject}</b> | Mode: <b>{mode}</b></div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Doubt enna bro? Type here or upload photo from sidebar..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare message payload
    contents = []
    for m in st.session_state.messages[:-1]:
        role = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

    # Current prompt parts (Text + Image if uploaded)
    current_parts = [types.Part.from_text(text=prompt)]
    if uploaded_image:
        image_bytes = uploaded_image.getvalue()
        current_parts.append(
            types.Part.from_bytes(data=image_bytes, mime_type=uploaded_image.type)
        )

    contents.append(types.Content(role="user", parts=current_parts))

    with st.chat_message("assistant"):
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            ),
        )
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})