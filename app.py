# Install if needed:
# pip install streamlit openai faiss-cpu python-dotenv langdetect PyMuPDF python-docx

import streamlit as st
from openai import OpenAI
import faiss
import numpy as np
import os
import time
from dotenv import load_dotenv
from langdetect import detect
import fitz  # For PDFs
import docx  # For DOCX

# 🌟 Set page config
st.set_page_config(page_title="Personal Analytical RAG Chatbot", page_icon="🤖", layout="wide")

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Sidebar
st.sidebar.subheader("🔄 Chat Controls")
reset_chat = st.sidebar.button("🔁 Reset Chat")
simulate_phd_interview = st.sidebar.button("🎓 Simulate PhD Interview")

# ===============================
# Load and Process Documents
# ===============================

# Load Tweets
translated_tweets_file = 'translated_tweets.txt'
if os.path.exists(translated_tweets_file):
    with open(translated_tweets_file, 'r', encoding='utf-8') as f:
        tweets = f.read().splitlines()
else:
    st.error("🚨 Translated tweets file not found!")
    st.stop()

# Load Personal Document
personal_text = ""
personal_doc_path = '/mnt/data/Roxana_Niksefat_Personal_Document.txt'
if os.path.exists(personal_doc_path):
    with open(personal_doc_path, 'r', encoding='utf-8') as file:
        personal_text = file.read()

# Load Thesis
thesis_text = ""
thesis_path = '/mnt/data/Trent___Roxana___MSc_Thesis (5).pdf'
if os.path.exists(thesis_path):
    with fitz.open(thesis_path) as doc:
        for page in doc:
            thesis_text += page.get_text()

# Upload Additional Files
uploaded_files = st.file_uploader(
    "📚 Upload additional files (PDF or DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

extracted_texts = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith('.pdf'):
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                extracted_texts.append("\n".join([page.get_text() for page in doc]))
        elif uploaded_file.name.endswith('.docx'):
            doc = docx.Document(uploaded_file)
            extracted_texts.append("\n".join([para.text for para in doc.paragraphs]))

combined_uploaded_text = "\n".join(extracted_texts)

# ===============================
# Chunked Summarization Function
# ===============================

def summarize_text(text, chunk_size=4000):
    if len(text) <= chunk_size:
        return text

    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    summarized_chunks = []

    for idx, chunk in enumerate(chunks):
        summarization_prompt = (
            "Summarize the following academic text into key research points, major findings, projects, and achievements. "
            "Limit the output to 300 words."
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": summarization_prompt},
                {"role": "user", "content": chunk}
            ]
        )

        summarized = response.choices[0].message.content.strip()
        summarized_chunks.append(summarized)

        time.sleep(1)

    final_summary = "\n\n".join(summarized_chunks)
    return final_summary

# Summarize large files
thesis_text = summarize_text(thesis_text)
combined_uploaded_text = summarize_text(combined_uploaded_text)

# Build context
context_text = "\n".join(f"- {tweet}" for tweet in tweets[:10])
if personal_text:
    context_text += f"\nPersonal Background:\n{personal_text}"
if thesis_text:
    context_text += f"\nMSc Thesis Summary:\n{thesis_text}"
if combined_uploaded_text:
    context_text += f"\nAdditional Uploaded Documents:\n{combined_uploaded_text}"

# ===============================
# Initialize Chat Session
# ===============================

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.phd_simulation_done = False
    st.session_state.simulate_phd = False

if reset_chat:
    st.session_state.messages = []
    st.session_state.phd_simulation_done = False
    st.session_state.simulate_phd = False
    st.success("✅ Chat reset!")

if simulate_phd_interview:
    st.session_state.simulate_phd = True

if not any(m.get("type") == "chatbot" for m in st.session_state.messages):
    st.session_state.messages.append({
        "role": "assistant",
        "type": "chatbot",
        "content": "👋 Welcome!\n\nI can assist you in **Persian 🇮🇷**, **English 🇬🇧**, or **French 🇫🇷**.\nFeel free to ask anything!"
    })

# ===============================
# Fast PhD Interview Simulation
# ===============================

if st.session_state.simulate_phd and not st.session_state.phd_simulation_done:
    st.session_state.messages.append({"role": "assistant", "type": "simulation", "content": "🎓 Starting PhD Interview Simulation!"})

    # Only 5 questions now!
    phd_questions = [
        "Can you describe your main research interests?",
        "What technical skills will help you during your PhD?",
        "Tell me about a major research challenge you faced.",
        "Where do you see your career after your PhD?",
        "Why do you want to join our department?"
    ]

    for question in phd_questions:
        st.session_state.messages.append({"role": "assistant", "type": "simulation", "content": f"🎓 **Professor:** {question}"})

        with st.spinner(f"🧑‍🎓 Answering: {question}"):
            system_prompt = (
                "You are Roxana Niksefat answering formally as a PhD applicant, based on your thesis, background, and projects."
            )

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Background:\n{context_text}\n\nQuestion:\n{question}"}
                ]
            )
            answer = response.choices[0].message.content.strip()
            st.session_state.messages.append({"role": "assistant", "type": "simulation", "content": f"🧑‍🎓 **Student:** {answer}"})

    st.session_state.phd_simulation_done = True
    st.session_state.simulate_phd = False  # Reset after finishing

# ===============================
# Display Chat History
# ===============================

for message in st.session_state.messages:
    role = message["role"]
    type_of_message = message.get("type", "chatbot")
    avatar = "👤" if role == "user" else ("🎓" if type_of_message == "simulation" else "🤖")

    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

# ===============================
# Normal Chatbot Input and Response
# ===============================

user_query = st.chat_input("Type your question here...")

def detect_language(text):
    try:
        lang = detect(text)
        if lang == 'fa':
            return "persian"
        elif lang == 'fr':
            return "french"
        else:
            return "english"
    except:
        return "english"

def translate_to_english(text, from_lang):
    if from_lang == "persian":
        instruction = "Translate this Persian text to English carefully."
    elif from_lang == "french":
        instruction = "Translate this French text to English carefully."
    else:
        return text

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()

if user_query:
    language = detect_language(user_query)
    if language != "english":
        user_query = translate_to_english(user_query, language)

    st.session_state.messages.append({"role": "user", "type": "chatbot", "content": user_query})

    system_prompt = (
        "You are a personal academic assistant for Roxana Niksefat. "
        "Answer user questions based only on the tweets, personal document, thesis, and uploaded documents."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Background:\n{context_text}\n\nQuestion:\n{user_query}"}
        ]
    )
    final_answer = response.choices[0].message.content.strip()
    st.session_state.messages.append({"role": "assistant", "type": "chatbot", "content": final_answer})

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Built for **Roxana Niksefat** ✨")
