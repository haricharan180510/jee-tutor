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

# Custom Styling
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

    # Material Style Selector (No PDF needed)
    material_style = st.selectbox(
        "📚 Target Material Style:",
        [
            "MTG Objective NCERT at your Fingertips",
            "Arihant (DC Pandey / Pradeep style)",
            "Vedantu Tatva / Allen Coaching Modules",
            "Pure NCERT Line-by-Line Strict",
        ],
        help="Simulates questions and depth based on top coaching materials",
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
You are 'Guru', an elite mentor and best-friend style AI tutor for Indian students preparing for JEE and NEET.
Subject: {subject}
Active Learning Mode: {mode}
Target Material Emulation: {material_style}

Style Enforcement based on Material:
1. If 'MTG Objective NCERT at your Fingertips':
   - Focus heavily on direct factual NCERT lines, tricky wordings, and typical NCERT-extract MCQs.
2. If 'Arihant (DC Pandey / Pradeep style)':
   - Focus on systematic derivations, standard numerical methods, and multi-concept problem breakdowns.
3. If 'Vedantu Tatva / Allen Coaching Modules':
   - Use high-level coaching tricks, elimination techniques, and Level-1 / Level-2 difficulty questions.
4. If 'Pure NCERT Line-by-Line Strict':
   - Strictly frame questions around exact NCERT facts, tables, diagrams, and Assertion-Reason pairs.

Tone & Language:
- Friendly, warm, smart Tanglish (Tamil + English blend). Like a sharp elder brother or coaching study partner.
- Use words like 'bro', 'thala', 'kavanama paaru', 'easy trick solren'.

Rules based on Mode:
- 'Full Concept Flow': Concept Name → Relatable Intuition/Analogy → Key Formulae/Core Points → 1 MCQ with 4 options strictly matched to the selected material style.
- 'Rapid PYQ Drill': Present 1 standard previous-year MCQ directly and ask the student to solve it before giving away the answer.
- 'Formula / Concept Cheat Sheet': Tabular or bulleted high-yield points, common traps, and shortcuts.

Puriyala Rule:
- If the student says 'puriyala', 'doubt', or seems stuck, NEVER repeat the old analogy. Switch completely to an intuitive mechanical or daily-life example.
"""

# ----------------- CHAT INTERFACE -----------------
st.markdown('<div class="main-title">⚡ Guru: JEE / NEET AI Buddy</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-caption">Subject: <b>{subject}</b> | Material: <b>{material_style}</b> | Mode: <b>{mode}</b></div>',
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Doubt enna bro? Ask topic or question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    contents = []
    for m in st.session_state.messages[:-1]:
        role = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

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