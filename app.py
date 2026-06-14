# """
# Student University Query Management System
# =========================================
# Uses RAG (Retrieval-Augmented Generation) to answer student questions
# from university documents using FAISS + Sentence Transformers + Gemini API.
# """

# import os
# from pathlib import Path

# import streamlit as st
# from dotenv import load_dotenv
# from rag_engine import build_index, search_chunks
# import google.generativeai as genai

# BASE_DIR = Path(__file__).resolve().parent

# # ── Load environment variables from .env file ──────────────────────────────
# load_dotenv(BASE_DIR / ".env")
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# # ── Configure Gemini ───────────────────────────────────────────────────────
# model = None
# if GEMINI_API_KEY:
#     genai.configure(api_key=GEMINI_API_KEY)
#     # model = genai.GenerativeModel("gemini-1.5-flash")
#     model = genai.GenerativeModel("gemini-2.5-flash")

# # ── Page config ────────────────────────────────────────────────────────────
# st.set_page_config(
#     page_title="UniQuery — Student Help Desk",
#     page_icon="🎓",
#     layout="centered",
# )

# # ── Custom CSS ─────────────────────────────────────────────────────────────
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Sora:wght@700;800&display=swap');

# html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

# /* Background */
# .stApp { background: #0f1117; }

# /* Hero banner */
# .hero {
#     background: linear-gradient(135deg, #1a1f2e 0%, #0f1117 60%);
#     border: 1px solid #2a2f3e;
#     border-radius: 16px;
#     padding: 36px 40px 28px;
#     margin-bottom: 28px;
#     position: relative;
#     overflow: hidden;
# }
# .hero::before {
#     content: '';
#     position: absolute;
#     top: -60px; right: -60px;
#     width: 220px; height: 220px;
#     background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%);
#     border-radius: 50%;
# }
# .hero-eyebrow {
#     font-size: 11px; font-weight: 600; letter-spacing: 2px;
#     color: #6366f1; text-transform: uppercase; margin-bottom: 10px;
# }
# .hero-title {
#     font-family: 'Sora', sans-serif;
#     font-size: 30px; font-weight: 800;
#     color: #f0f0f5; line-height: 1.2; margin-bottom: 12px;
# }
# .hero-title span { color: #6366f1; }
# .hero-desc {
#     font-size: 14px; color: #8b8fa8; line-height: 1.7; max-width: 520px;
# }

# /* How it works pills */
# .steps-row {
#     display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 28px;
# }
# .step-pill {
#     background: #1a1f2e; border: 1px solid #2a2f3e;
#     border-radius: 20px; padding: 6px 14px;
#     font-size: 12px; color: #8b8fa8;
#     display: flex; align-items: center; gap: 6px;
# }
# .step-pill b { color: #6366f1; font-size: 11px; }

# /* Input label */
# .q-label {
#     font-size: 13px; font-weight: 600;
#     color: #c5c7d4; margin-bottom: 8px; letter-spacing: 0.3px;
# }

# /* Answer card */
# .answer-card {
#     background: #1a1f2e;
#     border: 1px solid #2a2f3e;
#     border-left: 3px solid #6366f1;
#     border-radius: 12px;
#     padding: 22px 26px;
#     margin-top: 20px;
#     color: #d4d6e4;
#     font-size: 15px;
#     line-height: 1.75;
# }
# .answer-label {
#     font-size: 11px; font-weight: 600; letter-spacing: 1.5px;
#     color: #6366f1; text-transform: uppercase; margin-bottom: 10px;
# }

# /* Error card */
# .error-card {
#     background: #1f1520; border: 1px solid #3d1f2e;
#     border-radius: 12px; padding: 16px 20px;
#     color: #f87171; font-size: 14px; margin-top: 16px;
# }

# /* Hide default streamlit chrome */
# #MainMenu, footer, header { visibility: hidden; }
# </style>
# """, unsafe_allow_html=True)


# # ── Build FAISS index once (cached so it doesn't reload on every interaction)
# @st.cache_resource(show_spinner="Building knowledge index…")
# def load_index():
#     """Load the university doc and build FAISS vector index."""
#     return build_index(str(BASE_DIR / "university_info.txt"))


# def ask_gemini(context: str, question: str) -> str:
#     """Send retrieved context + student question to Gemini and get an answer."""
#     if not model:
#         return "Gemini is not configured because the API key is missing."

#     prompt = f"""You are a helpful university assistant.
# Use ONLY the context below to answer the student's question.
# If the answer is not in the context, say: "I don't have that information in the university documents."

# Context:
# {context}

# Student Question: {question}

# Answer in simple, clear language suitable for a student."""
#     response = model.generate_content(prompt)
#     return response.text


# # ── UI ─────────────────────────────────────────────────────────────────────

# # Hero
# st.markdown("""
# <div class="hero">
#     <div class="hero-eyebrow">🎓 RAG-Powered Help Desk</div>
#     <div class="hero-title">Student <span>University</span> Query System</div>
#     <div class="hero-desc">
#         Ask anything about admissions, fees, exam dates, syllabus, hostel rules,
#         library timings, placements, or scholarships. Answers are pulled directly
#         from official university documents.
#     </div>
# </div>
# """, unsafe_allow_html=True)

# # How it works
# st.markdown("""
# <div class="steps-row">
#     <div class="step-pill"><b>01</b> You ask a question</div>
#     <div class="step-pill"><b>02</b> FAISS finds relevant text</div>
#     <div class="step-pill"><b>03</b> Gemini generates the answer</div>
# </div>
# """, unsafe_allow_html=True)

# # Load index
# try:
#     chunks, index, embed_model = load_index()
# except FileNotFoundError:
#     st.markdown('<div class="error-card">⚠️ <b>university_info.txt</b> not found. Please place it in the project root.</div>', unsafe_allow_html=True)
#     st.stop()

# # Question input
# st.markdown('<div class="q-label">Your Question</div>', unsafe_allow_html=True)
# question = st.text_input(
#     label="question_input",
#     placeholder="e.g. What are the hostel rules? When is the last date to apply?",
#     label_visibility="collapsed",
# )

# ask = st.button("Ask →", type="primary", use_container_width=True)

# # Answer
# if ask:
#     if not question.strip():
#         st.warning("Please type a question first.")
#     elif not GEMINI_API_KEY:
#         st.markdown('<div class="error-card">⚠️ GEMINI_API_KEY missing in .env file.</div>', unsafe_allow_html=True)
#     else:
#         with st.spinner("Searching documents and generating answer…"):
#             # Step 1 — Retrieve relevant chunks from FAISS
#             relevant_chunks = search_chunks(question, chunks, index, embed_model, top_k=4)
#             context = "\n\n".join(relevant_chunks)

#             # Step 2 — Ask Gemini with context
#             answer = ask_gemini(context, question)

#         st.markdown(f"""
#         <div class="answer-card">
#             <div class="answer-label">Answer</div>
#             {answer}
#         </div>
#         """, unsafe_allow_html=True)

#         # Expandable: show which chunks were used (useful for demo)
#         with st.expander("📄 Source chunks retrieved from documents"):
#             for i, chunk in enumerate(relevant_chunks, 1):
#                 st.markdown(f"**Chunk {i}:**\n\n{chunk}\n\n---")
"""
Student University Query Management System
=========================================
RAG based student query system using FAISS + Sentence Transformers + Gemini API.
Only UI/CSS upgraded.
"""

# import os
# from pathlib import Path

# import streamlit as st
# from dotenv import load_dotenv
# from rag_engine import build_index, search_chunks
# import google.generativeai as genai

# BASE_DIR = Path(__file__).resolve().parent

# load_dotenv(BASE_DIR / ".env")
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# model = None
# if GEMINI_API_KEY:
#     genai.configure(api_key=GEMINI_API_KEY)
#     model = genai.GenerativeModel("gemini-2.5-flash")

# st.set_page_config(
#     page_title="UniQuery AI",
#     page_icon="🎓",
#     layout="wide",
# )

# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

# * {
#     font-family: 'Poppins', sans-serif;
# }

# .stApp {
#     background:
#         radial-gradient(circle at top left, rgba(99,102,241,0.22), transparent 35%),
#         radial-gradient(circle at bottom right, rgba(14,165,233,0.18), transparent 35%),
#         #070b14;
#     color: #ffffff;
# }

# #MainMenu, footer, header {
#     visibility: hidden;
# }

# .block-container {
#     padding-top: 2rem;
#     max-width: 1200px;
# }

# .hero {
#     background: linear-gradient(135deg, rgba(30,41,59,0.95), rgba(15,23,42,0.92));
#     border: 1px solid rgba(148,163,184,0.25);
#     border-radius: 28px;
#     padding: 42px;
#     box-shadow: 0 20px 60px rgba(0,0,0,0.35);
#     position: relative;
#     overflow: hidden;
# }

# .hero::after {
#     content: "";
#     position: absolute;
#     right: -80px;
#     top: -80px;
#     width: 260px;
#     height: 260px;
#     background: radial-gradient(circle, rgba(99,102,241,0.45), transparent 70%);
#     border-radius: 50%;
# }

# .badge {
#     display: inline-block;
#     background: rgba(99,102,241,0.18);
#     color: #a5b4fc;
#     border: 1px solid rgba(129,140,248,0.35);
#     padding: 8px 16px;
#     border-radius: 999px;
#     font-size: 13px;
#     font-weight: 600;
#     margin-bottom: 18px;
# }

# .hero h1 {
#     font-size: 46px;
#     line-height: 1.12;
#     margin: 0;
#     color: #f8fafc;
#     font-weight: 800;
# }

# .hero h1 span {
#     background: linear-gradient(90deg, #818cf8, #38bdf8);
#     -webkit-background-clip: text;
#     -webkit-text-fill-color: transparent;
# }

# .hero p {
#     margin-top: 18px;
#     font-size: 16px;
#     color: #cbd5e1;
#     max-width: 720px;
#     line-height: 1.8;
# }

# .stat-card {
#     background: rgba(15,23,42,0.82);
#     border: 1px solid rgba(148,163,184,0.22);
#     border-radius: 20px;
#     padding: 22px;
#     text-align: center;
#     box-shadow: 0 12px 35px rgba(0,0,0,0.25);
# }

# .stat-card h3 {
#     margin: 0;
#     color: #38bdf8;
#     font-size: 26px;
# }

# .stat-card p {
#     color: #94a3b8;
#     margin: 6px 0 0;
#     font-size: 13px;
# }

# .query-card {
#     margin-top: 28px;
#     background: rgba(15,23,42,0.86);
#     border: 1px solid rgba(148,163,184,0.22);
#     border-radius: 24px;
#     padding: 28px;
#     box-shadow: 0 18px 45px rgba(0,0,0,0.28);
# }

# .section-title {
#     font-size: 20px;
#     font-weight: 700;
#     color: #f8fafc;
#     margin-bottom: 6px;
# }

# .section-sub {
#     color: #94a3b8;
#     font-size: 14px;
#     margin-bottom: 18px;
# }

# .answer-card {
#     background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,41,59,0.92));
#     border: 1px solid rgba(56,189,248,0.35);
#     border-left: 5px solid #38bdf8;
#     border-radius: 22px;
#     padding: 28px;
#     margin-top: 26px;
#     color: #e2e8f0;
#     font-size: 16px;
#     line-height: 1.8;
#     box-shadow: 0 18px 45px rgba(0,0,0,0.35);
# }

# .answer-label {
#     color: #38bdf8;
#     font-size: 13px;
#     font-weight: 700;
#     letter-spacing: 1.5px;
#     text-transform: uppercase;
#     margin-bottom: 12px;
# }

# .error-card {
#     background: rgba(127,29,29,0.22);
#     border: 1px solid rgba(248,113,113,0.35);
#     color: #fecaca;
#     border-radius: 18px;
#     padding: 18px;
#     margin-top: 16px;
# }

# .info-box {
#     background: rgba(99,102,241,0.12);
#     border: 1px solid rgba(129,140,248,0.25);
#     border-radius: 16px;
#     padding: 18px;
#     color: #c7d2fe;
#     font-size: 14px;
#     line-height: 1.7;
# }

# div.stButton > button {
#     height: 52px;
#     border-radius: 16px;
#     font-weight: 700;
#     font-size: 16px;
#     background: linear-gradient(90deg, #4f46e5, #0ea5e9);
#     border: none;
#     color: white;
#     box-shadow: 0 12px 30px rgba(14,165,233,0.25);
# }

# div.stButton > button:hover {
#     transform: translateY(-1px);
#     box-shadow: 0 16px 35px rgba(14,165,233,0.35);
# }

# .stTextInput input {
#     background: rgba(2,6,23,0.85);
#     color: #f8fafc;
#     border: 1px solid rgba(148,163,184,0.3);
#     border-radius: 16px;
#     height: 54px;
# }

# .stTextInput input:focus {
#     border-color: #38bdf8;
# }

# [data-testid="stSidebar"] {
#     background: #020617;
#     border-right: 1px solid rgba(148,163,184,0.16);
# }

# .sidebar-title {
#     font-size: 24px;
#     font-weight: 800;
#     color: #f8fafc;
# }

# .sidebar-text {
#     color: #94a3b8;
#     font-size: 14px;
#     line-height: 1.7;
# }

# .small-pill {
#     display: inline-block;
#     background: rgba(56,189,248,0.12);
#     border: 1px solid rgba(56,189,248,0.25);
#     color: #7dd3fc;
#     padding: 6px 12px;
#     border-radius: 999px;
#     font-size: 12px;
#     margin: 4px 4px 4px 0;
# }
# </style>
# """, unsafe_allow_html=True)


# @st.cache_resource(show_spinner="Building university knowledge index...")
# def load_index():
#     return build_index(str(BASE_DIR / "university_info.txt"))


# def ask_gemini(context: str, question: str) -> str:
#     if not model:
#         return "Gemini is not configured because the API key is missing."

#     prompt = f"""You are a helpful university assistant.
# Use ONLY the context below to answer the student's question.
# If the answer is not in the context, say: "I don't have that information in the university documents."

# Context:
# {context}

# Student Question: {question}

# Answer in simple, clear language suitable for a student."""
    
#     response = model.generate_content(prompt)
#     return response.text


# with st.sidebar:
#     st.markdown('<div class="sidebar-title">🎓 UniQuery AI</div>', unsafe_allow_html=True)
#     st.markdown(
#         '<div class="sidebar-text">An AI-powered student help desk that answers questions from university documents using RAG.</div>',
#         unsafe_allow_html=True,
#     )

#     st.markdown("---")
#     st.markdown("### 🔍 Ask About")
#     st.markdown("""
#     <span class="small-pill">Admissions</span>
#     <span class="small-pill">Fees</span>
#     <span class="small-pill">Hostel</span>
#     <span class="small-pill">Library</span>
#     <span class="small-pill">Scholarship</span>
#     <span class="small-pill">Placement</span>
#     <span class="small-pill">Exams</span>
#     """, unsafe_allow_html=True)

#     st.markdown("---")
#     st.markdown("### ⚙️ System Status")

#     if GEMINI_API_KEY:
#         st.success("Gemini API Connected")
#     else:
#         st.error("Gemini API Missing")

#     st.info("FAISS + Sentence Transformers + Gemini")


# st.markdown("""
# <div class="hero">
#     <div class="badge">🚀 RAG Powered University Assistant</div>
#     <h1>Ask University Questions<br><span>Get Instant AI Answers</span></h1>
#     <p>
#         This smart help desk searches university documents using FAISS and generates
#         simple answers with Gemini AI. Useful for students asking about fees,
#         admission, hostel rules, exams, library, scholarships and placements.
#     </p>
# </div>
# """, unsafe_allow_html=True)

# st.write("")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.markdown("""
#     <div class="stat-card">
#         <h3>01</h3>
#         <p>Student asks question</p>
#     </div>
#     """, unsafe_allow_html=True)

# with col2:
#     st.markdown("""
#     <div class="stat-card">
#         <h3>02</h3>
#         <p>FAISS searches documents</p>
#     </div>
#     """, unsafe_allow_html=True)

# with col3:
#     st.markdown("""
#     <div class="stat-card">
#         <h3>03</h3>
#         <p>Gemini creates answer</p>
#     </div>
#     """, unsafe_allow_html=True)


# try:
#     chunks, index, embed_model = load_index()
# except FileNotFoundError:
#     st.markdown(
#         '<div class="error-card">⚠️ <b>university_info.txt</b> not found. Please place it in the project root folder.</div>',
#         unsafe_allow_html=True,
#     )
#     st.stop()


# st.markdown('<div class="query-card">', unsafe_allow_html=True)

# st.markdown('<div class="section-title">💬 Ask Your Question</div>', unsafe_allow_html=True)
# st.markdown(
#     '<div class="section-sub">Type any university-related question below.</div>',
#     unsafe_allow_html=True,
# )

# example_questions = [
#     "What are the hostel rules?",
#     "What is the library timing?",
#     "Tell me about scholarship details.",
#     "What are the placement rules?",
# ]

# selected_example = st.selectbox(
#     "Choose sample question",
#     [""] + example_questions,
# )

# question = st.text_input(
#     "Your Question",
#     value=selected_example,
#     placeholder="Example: What are the hostel rules?",
# )

# col_btn1, col_btn2 = st.columns([3, 1])

# with col_btn1:
#     ask = st.button("✨ Generate Answer", type="primary", use_container_width=True)

# with col_btn2:
#     clear = st.button("Clear", use_container_width=True)

# st.markdown("</div>", unsafe_allow_html=True)


# if clear:
#     st.rerun()


# if ask:
#     if not question.strip():
#         st.warning("Please type a question first.")

#     elif not GEMINI_API_KEY:
#         st.markdown(
#             '<div class="error-card">⚠️ GEMINI_API_KEY is missing. Please add it in your .env file.</div>',
#             unsafe_allow_html=True,
#         )

#     else:
#         with st.spinner("Searching university documents and generating answer..."):
#             relevant_chunks = search_chunks(
#                 question,
#                 chunks,
#                 index,
#                 embed_model,
#                 top_k=4
#             )

#             context = "\n\n".join(relevant_chunks)
#             answer = ask_gemini(context, question)

#         st.markdown(f"""
#         <div class="answer-card">
#             <div class="answer-label">AI Answer</div>
#             {answer}
#         </div>
#         """, unsafe_allow_html=True)

#         st.success("Answer generated successfully.")

#         with st.expander("📄 View source chunks used by RAG"):
#             for i, chunk in enumerate(relevant_chunks, 1):
#                 st.markdown(f"### Chunk {i}")
#                 st.write(chunk)
#                 st.markdown("---")

#         with st.expander("🧠 How this answer was generated"):
#             st.markdown("""
#             <div class="info-box">
#                 <b>Step 1:</b> Your question was converted into embeddings.<br>
#                 <b>Step 2:</b> FAISS searched the most relevant document chunks.<br>
#                 <b>Step 3:</b> Gemini used only those chunks to generate the answer.<br>
#                 <b>Step 4:</b> The final answer was shown in simple student-friendly language.
#             </div>
#             """, unsafe_allow_html=True)
# """
# # Student University Query Management System
# # =========================================
# # RAG based student query system using FAISS + Sentence Transformers + Gemini API.
# # UI upgraded + Enter key submit feature added.
# # """

# import os
# from pathlib import Path

# import streamlit as st
# from dotenv import load_dotenv
# from rag_engine import build_index, search_chunks
# import google.generativeai as genai

# BASE_DIR = Path(__file__).resolve().parent

# load_dotenv(BASE_DIR / ".env")
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# model = None
# if GEMINI_API_KEY:
#     genai.configure(api_key=GEMINI_API_KEY)
#     model = genai.GenerativeModel("gemini-2.5-flash")

# st.set_page_config(
#     page_title="UniQuery AI",
#     page_icon="🎓",
#     layout="wide",
# )

# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

# * {
#     font-family: 'Poppins', sans-serif;
# }

# .stApp {
#     background:
#         radial-gradient(circle at top left, rgba(99,102,241,0.22), transparent 35%),
#         radial-gradient(circle at bottom right, rgba(14,165,233,0.18), transparent 35%),
#         #070b14;
#     color: #ffffff;
# }

# #MainMenu, footer, header {
#     visibility: hidden;
# }

# .block-container {
#     padding-top: 2rem;
#     max-width: 1200px;
# }

# .hero {
#     background: linear-gradient(135deg, rgba(30,41,59,0.95), rgba(15,23,42,0.92));
#     border: 1px solid rgba(148,163,184,0.25);
#     border-radius: 28px;
#     padding: 42px;
#     box-shadow: 0 20px 60px rgba(0,0,0,0.35);
#     position: relative;
#     overflow: hidden;
# }

# .hero::after {
#     content: "";
#     position: absolute;
#     right: -80px;
#     top: -80px;
#     width: 260px;
#     height: 260px;
#     background: radial-gradient(circle, rgba(99,102,241,0.45), transparent 70%);
#     border-radius: 50%;
# }

# .badge {
#     display: inline-block;
#     background: rgba(99,102,241,0.18);
#     color: #a5b4fc;
#     border: 1px solid rgba(129,140,248,0.35);
#     padding: 8px 16px;
#     border-radius: 999px;
#     font-size: 13px;
#     font-weight: 600;
#     margin-bottom: 18px;
# }

# .hero h1 {
#     font-size: 46px;
#     line-height: 1.12;
#     margin: 0;
#     color: #f8fafc;
#     font-weight: 800;
# }

# .hero h1 span {
#     background: linear-gradient(90deg, #818cf8, #38bdf8);
#     -webkit-background-clip: text;
#     -webkit-text-fill-color: transparent;
# }

# .hero p {
#     margin-top: 18px;
#     font-size: 16px;
#     color: #cbd5e1;
#     max-width: 720px;
#     line-height: 1.8;
# }

# .stat-card {
#     background: rgba(15,23,42,0.82);
#     border: 1px solid rgba(148,163,184,0.22);
#     border-radius: 20px;
#     padding: 22px;
#     text-align: center;
#     box-shadow: 0 12px 35px rgba(0,0,0,0.25);
# }

# .stat-card h3 {
#     margin: 0;
#     color: #38bdf8;
#     font-size: 26px;
# }

# .stat-card p {
#     color: #94a3b8;
#     margin: 6px 0 0;
#     font-size: 13px;
# }

# .query-card {
#     margin-top: 28px;
#     background: rgba(15,23,42,0.86);
#     border: 1px solid rgba(148,163,184,0.22);
#     border-radius: 24px;
#     padding: 28px;
#     box-shadow: 0 18px 45px rgba(0,0,0,0.28);
# }

# .section-title {
#     font-size: 20px;
#     font-weight: 700;
#     color: #f8fafc;
#     margin-bottom: 6px;
# }

# .section-sub {
#     color: #94a3b8;
#     font-size: 14px;
#     margin-bottom: 18px;
# }

# .answer-card {
#     background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,41,59,0.92));
#     border: 1px solid rgba(56,189,248,0.35);
#     border-left: 5px solid #38bdf8;
#     border-radius: 22px;
#     padding: 28px;
#     margin-top: 26px;
#     color: #e2e8f0;
#     font-size: 16px;
#     line-height: 1.8;
#     box-shadow: 0 18px 45px rgba(0,0,0,0.35);
# }

# .answer-label {
#     color: #38bdf8;
#     font-size: 13px;
#     font-weight: 700;
#     letter-spacing: 1.5px;
#     text-transform: uppercase;
#     margin-bottom: 12px;
# }

# .error-card {
#     background: rgba(127,29,29,0.22);
#     border: 1px solid rgba(248,113,113,0.35);
#     color: #fecaca;
#     border-radius: 18px;
#     padding: 18px;
#     margin-top: 16px;
# }

# .info-box {
#     background: rgba(99,102,241,0.12);
#     border: 1px solid rgba(129,140,248,0.25);
#     border-radius: 16px;
#     padding: 18px;
#     color: #c7d2fe;
#     font-size: 14px;
#     line-height: 1.7;
# }

# div.stButton > button,
# div.stFormSubmitButton > button {
#     height: 52px;
#     border-radius: 16px;
#     font-weight: 700;
#     font-size: 16px;
#     background: linear-gradient(90deg, #4f46e5, #0ea5e9);
#     border: none;
#     color: white;
#     box-shadow: 0 12px 30px rgba(14,165,233,0.25);
# }

# div.stButton > button:hover,
# div.stFormSubmitButton > button:hover {
#     transform: translateY(-1px);
#     box-shadow: 0 16px 35px rgba(14,165,233,0.35);
# }

# .stTextInput input {
#     background: rgba(2,6,23,0.85);
#     color: #f8fafc;
#     border: 1px solid rgba(148,163,184,0.3);
#     border-radius: 16px;
#     height: 54px;
# }

# .stTextInput input:focus {
#     border-color: #38bdf8;
# }

# [data-testid="stSidebar"] {
#     background: #020617;
#     border-right: 1px solid rgba(148,163,184,0.16);
# }

# .sidebar-title {
#     font-size: 24px;
#     font-weight: 800;
#     color: #f8fafc;
# }

# .sidebar-text {
#     color: #94a3b8;
#     font-size: 14px;
#     line-height: 1.7;
# }

# .small-pill {
#     display: inline-block;
#     background: rgba(56,189,248,0.12);
#     border: 1px solid rgba(56,189,248,0.25);
#     color: #7dd3fc;
#     padding: 6px 12px;
#     border-radius: 999px;
#     font-size: 12px;
#     margin: 4px 4px 4px 0;
# }
# </style>
# """, unsafe_allow_html=True)


# @st.cache_resource(show_spinner="Building university knowledge index...")
# def load_index():
#     return build_index(str(BASE_DIR / "university_info.txt"))


# def ask_gemini(context: str, question: str) -> str:
#     if not model:
#         return "Gemini is not configured because the API key is missing."

#     prompt = f"""You are a helpful university assistant.
# Use ONLY the context below to answer the student's question.
# If the answer is not in the context, say: "I don't have that information in the university documents."

# Context:
# {context}

# Student Question: {question}

# Answer in simple, clear language suitable for a student."""

#     response = model.generate_content(prompt)
#     return response.text


# with st.sidebar:
#     st.markdown('<div class="sidebar-title">🎓 UniQuery AI</div>', unsafe_allow_html=True)
#     st.markdown(
#         '<div class="sidebar-text">An AI-powered student help desk that answers questions from university documents using RAG.</div>',
#         unsafe_allow_html=True,
#     )

#     st.markdown("---")
#     st.markdown("### 🔍 Ask About")
#     st.markdown("""
#     <span class="small-pill">Admissions</span>
#     <span class="small-pill">Fees</span>
#     <span class="small-pill">Hostel</span>
#     <span class="small-pill">Library</span>
#     <span class="small-pill">Scholarship</span>
#     <span class="small-pill">Placement</span>
#     <span class="small-pill">Exams</span>
#     """, unsafe_allow_html=True)

#     st.markdown("---")
#     st.markdown("### ⚙️ System Status")

#     if GEMINI_API_KEY:
#         st.success("Gemini API Connected")
#     else:
#         st.error("Gemini API Missing")

#     st.info("FAISS + Sentence Transformers + Gemini")


# st.markdown("""
# <div class="hero">
#     <div class="badge">🚀 RAG Powered University Assistant</div>
#     <h1>Ask University Questions<br><span>Get Instant AI Answers</span></h1>
#     <p>
#         This smart help desk searches university documents using FAISS and generates
#         simple answers with Gemini AI. Useful for students asking about fees,
#         admission, hostel rules, exams, library, scholarships and placements.
#     </p>
# </div>
# """, unsafe_allow_html=True)

# st.write("")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.markdown("""
#     <div class="stat-card">
#         <h3>01</h3>
#         <p>Student asks question</p>
#     </div>
#     """, unsafe_allow_html=True)

# with col2:
#     st.markdown("""
#     <div class="stat-card">
#         <h3>02</h3>
#         <p>FAISS searches documents</p>
#     </div>
#     """, unsafe_allow_html=True)

# with col3:
#     st.markdown("""
#     <div class="stat-card">
#         <h3>03</h3>
#         <p>Gemini creates answer</p>
#     </div>
#     """, unsafe_allow_html=True)


# try:
#     chunks, index, embed_model = load_index()
# except FileNotFoundError:
#     st.markdown(
#         '<div class="error-card">⚠️ <b>university_info.txt</b> not found. Please place it in the project root folder.</div>',
#         unsafe_allow_html=True,
#     )
#     st.stop()


# st.markdown('<div class="query-card">', unsafe_allow_html=True)

# st.markdown('<div class="section-title">💬 Ask Your Question</div>', unsafe_allow_html=True)
# st.markdown(
#     '<div class="section-sub">Type your question and press Enter, or click Generate Answer.</div>',
#     unsafe_allow_html=True,
# )

# example_questions = [
#     "What are the hostel rules?",
#     "What is the library timing?",
#     "Tell me about scholarship details.",
#     "What are the placement rules?",
# ]

# selected_example = st.selectbox(
#     "Choose sample question",
#     [""] + example_questions,
# )

# with st.form("question_form", clear_on_submit=False):
#     question = st.text_input(
#         "Your Question",
#         value=selected_example,
#         placeholder="Example: What are the hostel rules?",
#     )

#     ask = st.form_submit_button(
#         "✨ Generate Answer",
#         type="primary",
#         use_container_width=True
#     )

# clear = st.button("Clear Question", use_container_width=True)

# st.markdown("</div>", unsafe_allow_html=True)


# if clear:
#     st.rerun()


# if ask:
#     if not question.strip():
#         st.warning("Please type a question first.")

#     elif not GEMINI_API_KEY:
#         st.markdown(
#             '<div class="error-card">⚠️ GEMINI_API_KEY is missing. Please add it in your .env file.</div>',
#             unsafe_allow_html=True,
#         )

#     else:
#         with st.spinner("Searching university documents and generating answer..."):
#             relevant_chunks = search_chunks(
#                 question,
#                 chunks,
#                 index,
#                 embed_model,
#                 top_k=4
#             )

#             context = "\n\n".join(relevant_chunks)
#             answer = ask_gemini(context, question)

#         st.markdown(f"""
#         <div class="answer-card">
#             <div class="answer-label">AI Answer</div>
#             {answer}
#         </div>
#         """, unsafe_allow_html=True)

#         st.success("Answer generated successfully.")

#         with st.expander("📄 View source chunks used by RAG"):
#             for i, chunk in enumerate(relevant_chunks, 1):
#                 st.markdown(f"### Chunk {i}")
#                 st.write(chunk)
#                 st.markdown("---")

#         with st.expander("🧠 How this answer was generated"):
#             st.markdown("""
#             <div class="info-box">
#                 <b>Step 1:</b> Your question was converted into embeddings.<br>
#                 <b>Step 2:</b> FAISS searched the most relevant document chunks.<br>
#                 <b>Step 3:</b> Gemini used only those chunks to generate the answer.<br>
#                 <b>Step 4:</b> The final answer was shown in simple student-friendly language.
#             </div>
#             """, unsafe_allow_html=True)
# """
# # Student University Query Management System
# # =========================================
# # RAG based student query system using FAISS + Sentence Transformers + Gemini API.
# # UI upgraded + Enter key + functional topic buttons.
# # """

# import os
# from pathlib import Path

# import streamlit as st
# from dotenv import load_dotenv
# from rag_engine import build_index, search_chunks
# import google.generativeai as genai

# BASE_DIR = Path(__file__).resolve().parent

# load_dotenv(BASE_DIR / ".env")
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# model = None
# if GEMINI_API_KEY:
#     genai.configure(api_key=GEMINI_API_KEY)
#     model = genai.GenerativeModel("gemini-2.5-flash")

# st.set_page_config(
#     page_title="UniQuery AI",
#     page_icon="🎓",
#     layout="wide",
# )

# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

# * {
#     font-family: 'Poppins', sans-serif;
# }

# .stApp {
#     background:
#         radial-gradient(circle at top left, rgba(99,102,241,0.22), transparent 35%),
#         radial-gradient(circle at bottom right, rgba(14,165,233,0.18), transparent 35%),
#         #070b14;
#     color: #ffffff;
# }

# #MainMenu, footer, header {
#     visibility: hidden;
# }

# .block-container {
#     padding-top: 2rem;
#     max-width: 1200px;
# }

# .hero {
#     background: linear-gradient(135deg, rgba(30,41,59,0.95), rgba(15,23,42,0.92));
#     border: 1px solid rgba(148,163,184,0.25);
#     border-radius: 28px;
#     padding: 42px;
#     box-shadow: 0 20px 60px rgba(0,0,0,0.35);
#     position: relative;
#     overflow: hidden;
# }

# .hero::after {
#     content: "";
#     position: absolute;
#     right: -80px;
#     top: -80px;
#     width: 260px;
#     height: 260px;
#     background: radial-gradient(circle, rgba(99,102,241,0.45), transparent 70%);
#     border-radius: 50%;
# }

# .badge {
#     display: inline-block;
#     background: rgba(99,102,241,0.18);
#     color: #a5b4fc;
#     border: 1px solid rgba(129,140,248,0.35);
#     padding: 8px 16px;
#     border-radius: 999px;
#     font-size: 13px;
#     font-weight: 600;
#     margin-bottom: 18px;
# }

# .hero h1 {
#     font-size: 46px;
#     line-height: 1.12;
#     margin: 0;
#     color: #f8fafc;
#     font-weight: 800;
# }

# .hero h1 span {
#     background: linear-gradient(90deg, #818cf8, #38bdf8);
#     -webkit-background-clip: text;
#     -webkit-text-fill-color: transparent;
# }

# .hero p {
#     margin-top: 18px;
#     font-size: 16px;
#     color: #cbd5e1;
#     max-width: 720px;
#     line-height: 1.8;
# }

# .stat-card {
#     background: rgba(15,23,42,0.82);
#     border: 1px solid rgba(148,163,184,0.22);
#     border-radius: 20px;
#     padding: 22px;
#     text-align: center;
#     box-shadow: 0 12px 35px rgba(0,0,0,0.25);
# }

# .stat-card h3 {
#     margin: 0;
#     color: #38bdf8;
#     font-size: 26px;
# }

# .stat-card p {
#     color: #94a3b8;
#     margin: 6px 0 0;
#     font-size: 13px;
# }

# .query-card {
#     margin-top: 28px;
#     background: rgba(15,23,42,0.86);
#     border: 1px solid rgba(148,163,184,0.22);
#     border-radius: 24px;
#     padding: 28px;
#     box-shadow: 0 18px 45px rgba(0,0,0,0.28);
# }

# .section-title {
#     font-size: 20px;
#     font-weight: 700;
#     color: #f8fafc;
#     margin-bottom: 6px;
# }

# .section-sub {
#     color: #94a3b8;
#     font-size: 14px;
#     margin-bottom: 18px;
# }

# .answer-card {
#     background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,41,59,0.92));
#     border: 1px solid rgba(56,189,248,0.35);
#     border-left: 5px solid #38bdf8;
#     border-radius: 22px;
#     padding: 28px;
#     margin-top: 26px;
#     color: #e2e8f0;
#     font-size: 16px;
#     line-height: 1.8;
#     box-shadow: 0 18px 45px rgba(0,0,0,0.35);
# }

# .answer-label {
#     color: #38bdf8;
#     font-size: 13px;
#     font-weight: 700;
#     letter-spacing: 1.5px;
#     text-transform: uppercase;
#     margin-bottom: 12px;
# }

# .error-card {
#     background: rgba(127,29,29,0.22);
#     border: 1px solid rgba(248,113,113,0.35);
#     color: #fecaca;
#     border-radius: 18px;
#     padding: 18px;
#     margin-top: 16px;
# }

# .info-box {
#     background: rgba(99,102,241,0.12);
#     border: 1px solid rgba(129,140,248,0.25);
#     border-radius: 16px;
#     padding: 18px;
#     color: #c7d2fe;
#     font-size: 14px;
#     line-height: 1.7;
# }

# div.stButton > button,
# div.stFormSubmitButton > button {
#     height: 52px;
#     border-radius: 16px;
#     font-weight: 700;
#     font-size: 15px;
#     background: linear-gradient(90deg, #4f46e5, #0ea5e9);
#     border: none;
#     color: white;
#     box-shadow: 0 12px 30px rgba(14,165,233,0.25);
# }

# div.stButton > button:hover,
# div.stFormSubmitButton > button:hover {
#     transform: translateY(-1px);
#     box-shadow: 0 16px 35px rgba(14,165,233,0.35);
# }

# .stTextInput input {
#     background: rgba(2,6,23,0.85);
#     color: #f8fafc;
#     border: 1px solid rgba(148,163,184,0.3);
#     border-radius: 16px;
#     height: 54px;
# }

# .stTextInput input:focus {
#     border-color: #38bdf8;
# }

# [data-testid="stSidebar"] {
#     background: #020617;
#     border-right: 1px solid rgba(148,163,184,0.16);
# }

# .sidebar-title {
#     font-size: 24px;
#     font-weight: 800;
#     color: #f8fafc;
# }

# .sidebar-text {
#     color: #94a3b8;
#     font-size: 14px;
#     line-height: 1.7;
# }
# </style>
# """, unsafe_allow_html=True)


# @st.cache_resource(show_spinner="Building university knowledge index...")
# def load_index():
#     return build_index(str(BASE_DIR / "university_info.txt"))


# def ask_gemini(context: str, question: str) -> str:
#     if not model:
#         return "Gemini is not configured because the API key is missing."

#     prompt = f"""You are a helpful university assistant.
# Use ONLY the context below to answer the student's question.
# If the answer is not in the context, say: "I don't have that information in the university documents."

# Context:
# {context}

# Student Question: {question}

# Answer in simple, clear language suitable for a student."""

#     response = model.generate_content(prompt)
#     return response.text


# def generate_answer(question):
#     relevant_chunks = search_chunks(
#         question,
#         chunks,
#         index,
#         embed_model,
#         top_k=4
#     )

#     context = "\n\n".join(relevant_chunks)
#     answer = ask_gemini(context, question)

#     st.session_state["answer"] = answer
#     st.session_state["relevant_chunks"] = relevant_chunks
#     st.session_state["last_question"] = question


# if "question" not in st.session_state:
#     st.session_state["question"] = ""

# if "answer" not in st.session_state:
#     st.session_state["answer"] = ""

# if "relevant_chunks" not in st.session_state:
#     st.session_state["relevant_chunks"] = []

# if "last_question" not in st.session_state:
#     st.session_state["last_question"] = ""


# try:
#     chunks, index, embed_model = load_index()
# except FileNotFoundError:
#     st.markdown(
#         '<div class="error-card">⚠️ <b>university_info.txt</b> not found. Please place it in the project root folder.</div>',
#         unsafe_allow_html=True,
#     )
#     st.stop()


# with st.sidebar:
#     st.markdown('<div class="sidebar-title">🎓 UniQuery AI</div>', unsafe_allow_html=True)
#     st.markdown(
#         '<div class="sidebar-text">Click any topic button below to ask automatically.</div>',
#         unsafe_allow_html=True,
#     )

#     st.markdown("---")
#     st.markdown("### 🔍 Quick Topic Buttons")

#     topic_questions = {
#         "🎓 Admission": "Tell me about the admission process.",
#         "💰 Fees": "Tell me about the university fee structure.",
#         "🏠 Hostel": "What are the hostel rules?",
#         "📚 Library": "What are the library timings and rules?",
#         "🎁 Scholarship": "Tell me about scholarship details.",
#         "💼 Placement": "Tell me about placement rules and opportunities.",
#         "📝 Exams": "Tell me about exam rules and important exam information.",
#     }

#     for button_name, button_question in topic_questions.items():
#         if st.button(button_name, use_container_width=True):
#             st.session_state["question"] = button_question

#             if not GEMINI_API_KEY:
#                 st.session_state["answer"] = "GEMINI_API_KEY is missing. Please add it in your .env file."
#                 st.session_state["last_question"] = button_question
#             else:
#                 with st.spinner(f"Generating answer for {button_name}..."):
#                     generate_answer(button_question)

#     st.markdown("---")
#     st.markdown("### ⚙️ System Status")

#     if GEMINI_API_KEY:
#         st.success("Gemini API Connected")
#     else:
#         st.error("Gemini API Missing")

#     st.info("FAISS + Sentence Transformers + Gemini")


# st.markdown("""
# <div class="hero">
#     <div class="badge">🚀 RAG Powered University Assistant</div>
#     <h1>Ask University Questions<br><span>Get Instant AI Answers</span></h1>
#     <p>
#         This smart help desk searches university documents using FAISS and generates
#         simple answers with Gemini AI. Useful for students asking about fees,
#         admission, hostel rules, exams, library, scholarships and placements.
#     </p>
# </div>
# """, unsafe_allow_html=True)

# st.write("")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.markdown("""
#     <div class="stat-card">
#         <h3>01</h3>
#         <p>Student asks question</p>
#     </div>
#     """, unsafe_allow_html=True)

# with col2:
#     st.markdown("""
#     <div class="stat-card">
#         <h3>02</h3>
#         <p>FAISS searches documents</p>
#     </div>
#     """, unsafe_allow_html=True)

# with col3:
#     st.markdown("""
#     <div class="stat-card">
#         <h3>03</h3>
#         <p>Gemini creates answer</p>
#     </div>
#     """, unsafe_allow_html=True)


# st.markdown('<div class="query-card">', unsafe_allow_html=True)

# st.markdown('<div class="section-title">💬 Ask Your Question</div>', unsafe_allow_html=True)
# st.markdown(
#     '<div class="section-sub">Type your question and press Enter, click Generate Answer, or use sidebar topic buttons.</div>',
#     unsafe_allow_html=True,
# )

# example_questions = [
#     "What are the hostel rules?",
#     "What is the library timing?",
#     "Tell me about scholarship details.",
#     "What are the placement rules?",
# ]

# selected_example = st.selectbox(
#     "Choose sample question",
#     [""] + example_questions,
# )

# if selected_example:
#     st.session_state["question"] = selected_example

# with st.form("question_form", clear_on_submit=False):
#     question = st.text_input(
#         "Your Question",
#         value=st.session_state["question"],
#         placeholder="Example: What are the hostel rules?",
#     )

#     ask = st.form_submit_button(
#         "✨ Generate Answer",
#         type="primary",
#         use_container_width=True
#     )

# clear = st.button("Clear Question", use_container_width=True)

# st.markdown("</div>", unsafe_allow_html=True)


# if clear:
#     st.session_state["question"] = ""
#     st.session_state["answer"] = ""
#     st.session_state["relevant_chunks"] = []
#     st.session_state["last_question"] = ""
#     st.rerun()


# if ask:
#     st.session_state["question"] = question

#     if not question.strip():
#         st.warning("Please type a question first.")

#     elif not GEMINI_API_KEY:
#         st.markdown(
#             '<div class="error-card">⚠️ GEMINI_API_KEY is missing. Please add it in your .env file.</div>',
#             unsafe_allow_html=True,
#         )

#     else:
#         with st.spinner("Searching university documents and generating answer..."):
#             generate_answer(question)


# if st.session_state["answer"]:
#     st.markdown(f"""
#     <div class="answer-card">
#         <div class="answer-label">AI Answer</div>
#         <b>Question:</b> {st.session_state["last_question"]}<br><br>
#         {st.session_state["answer"]}
#     </div>
#     """, unsafe_allow_html=True)

#     st.success("Answer generated successfully.")

#     with st.expander("📄 View source chunks used by RAG"):
#         for i, chunk in enumerate(st.session_state["relevant_chunks"], 1):
#             st.markdown(f"### Chunk {i}")
#             st.write(chunk)
#             st.markdown("---")

#     with st.expander("🧠 How this answer was generated"):
#         st.markdown("""
#         <div class="info-box">
#             <b>Step 1:</b> Your question was converted into embeddings.<br>
#             <b>Step 2:</b> FAISS searched the most relevant document chunks.<br>
#             <b>Step 3:</b> Gemini used only those chunks to generate the answer.<br>
#             <b>Step 4:</b> The final answer was shown in simple student-friendly language.
#         </div>
#         """, unsafe_allow_html=True)

# kokejeihii




import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from rag_engine import build_index, search_chunks
import google.generativeai as genai

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(
    page_title="UniQuery AI",
    page_icon="🎓",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(99,102,241,0.22), transparent 35%),
        radial-gradient(circle at bottom right, rgba(14,165,233,0.18), transparent 35%),
        #070b14;
    color: #ffffff;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

.hero {
    background: linear-gradient(135deg, rgba(30,41,59,0.95), rgba(15,23,42,0.92));
    border: 1px solid rgba(148,163,184,0.25);
    border-radius: 28px;
    padding: 42px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.35);
    position: relative;
    overflow: hidden;
}

.hero::after {
    content: "";
    position: absolute;
    right: -80px;
    top: -80px;
    width: 260px;
    height: 260px;
    background: radial-gradient(circle, rgba(99,102,241,0.45), transparent 70%);
    border-radius: 50%;
}

.badge {
    display: inline-block;
    background: rgba(99,102,241,0.18);
    color: #a5b4fc;
    border: 1px solid rgba(129,140,248,0.35);
    padding: 8px 16px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 18px;
}

.hero h1 {
    font-size: 34px;
    line-height: 1.2;
    margin: 0;
    color: #f8fafc;
    font-weight: 800;
}

@media (max-width: 768px) {
    .hero h1 {
        font-size: 26px;
    }
}

.hero h1 span {
    background: linear-gradient(90deg, #818cf8, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    margin-top: 18px;
    font-size: 16px;
    color: #cbd5e1;
    max-width: 720px;
    line-height: 1.8;
}

.stat-card {
    background: rgba(15,23,42,0.82);
    border: 1px solid rgba(148,163,184,0.22);
    border-radius: 20px;
    padding: 22px;
    text-align: center;
    box-shadow: 0 12px 35px rgba(0,0,0,0.25);
}

.stat-card h3 {
    margin: 0;
    color: #38bdf8;
    font-size: 26px;
}

.stat-card p {
    color: #94a3b8;
    margin: 6px 0 0;
    font-size: 13px;
}

.query-card {
    margin-top: 28px;
    background: rgba(15,23,42,0.86);
    border: 1px solid rgba(148,163,184,0.22);
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 18px 45px rgba(0,0,0,0.28);
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 6px;
}

.section-sub {
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 18px;
}

.answer-card {
    background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,41,59,0.92));
    border: 1px solid rgba(56,189,248,0.35);
    border-left: 5px solid #38bdf8;
    border-radius: 22px;
    padding: 28px;
    margin-top: 26px;
    color: #e2e8f0;
    font-size: 16px;
    line-height: 1.8;
    box-shadow: 0 18px 45px rgba(0,0,0,0.35);
}

.answer-label {
    color: #38bdf8;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.error-card {
    background: rgba(127,29,29,0.22);
    border: 1px solid rgba(248,113,113,0.35);
    color: #fecaca;
    border-radius: 18px;
    padding: 18px;
    margin-top: 16px;
}

.info-box {
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(129,140,248,0.25);
    border-radius: 16px;
    padding: 18px;
    color: #c7d2fe;
    font-size: 14px;
    line-height: 1.7;
}

div.stButton > button,
div.stFormSubmitButton > button {
    height: 52px;
    border-radius: 16px;
    font-weight: 700;
    font-size: 15px;
    background: linear-gradient(90deg, #4f46e5, #0ea5e9);
    border: none;
    color: white;
    box-shadow: 0 12px 30px rgba(14,165,233,0.25);
}

div.stButton > button:hover,
div.stFormSubmitButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 16px 35px rgba(14,165,233,0.35);
}

.stTextInput input {
    background: rgba(2,6,23,0.85);
    color: #f8fafc;
    border: 1px solid rgba(148,163,184,0.3);
    border-radius: 16px;
    height: 54px;
}

.stTextInput input:focus {
    border-color: #38bdf8;
}

[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid rgba(148,163,184,0.16);
}

.sidebar-title {
    font-size: 24px;
    font-weight: 800;
    color: #f8fafc;
}

.sidebar-text {
    color: #94a3b8;
    font-size: 14px;
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Building university knowledge index...")
def load_index():
    return build_index(str(BASE_DIR / "university_info.txt"))


def ask_gemini(context: str, question: str) -> str:
    if not model:
        return "Gemini is not configured because the API key is missing."

    prompt = f"""You are a helpful university assistant.
Use ONLY the context below to answer the student's question.
If the answer is not in the context, say: "I don't have that information in the university documents."

Context:
{context}

Student Question: {question}

Answer in simple, clear language suitable for a student."""

    response = model.generate_content(prompt)
    return response.text


def generate_answer(question):
    relevant_chunks = search_chunks(
        question,
        chunks,
        index,
        embed_model,
        top_k=4
    )

    context = "\n\n".join(relevant_chunks)
    answer = ask_gemini(context, question)

    st.session_state["answer"] = answer
    st.session_state["relevant_chunks"] = relevant_chunks
    st.session_state["last_question"] = question


if "question" not in st.session_state:
    st.session_state["question"] = ""

if "answer" not in st.session_state:
    st.session_state["answer"] = ""

if "relevant_chunks" not in st.session_state:
    st.session_state["relevant_chunks"] = []

if "last_question" not in st.session_state:
    st.session_state["last_question"] = ""


try:
    chunks, index, embed_model = load_index()
except FileNotFoundError:
    st.markdown(
        '<div class="error-card">⚠️ <b>university_info.txt</b> not found. Please place it in the project root folder.</div>',
        unsafe_allow_html=True,
    )
    st.stop()


with st.sidebar:
    st.markdown('<div class="sidebar-title">🎓 UniQuery AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-text">Click any topic button below to ask automatically.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### 🔍 Quick Topic Buttons")

    topic_questions = {
        "🎓 Admission": "Tell me about the admission process.",
        "💰 Fees": "Tell me about the university fee structure.",
        "🏠 Hostel": "What are the hostel rules?",
        "📚 Library": "What are the library timings and rules?",
        "🎁 Scholarship": "Tell me about scholarship details.",
        "💼 Placement": "Tell me about placement rules and opportunities.",
        "📝 Exams": "Tell me about exam rules and important exam information.",
    }

    for button_name, button_question in topic_questions.items():
        if st.button(button_name, use_container_width=True):
            st.session_state["question"] = button_question

            if not GEMINI_API_KEY:
                st.session_state["answer"] = "GEMINI_API_KEY is missing. Please add it in your .env file."
                st.session_state["last_question"] = button_question
            else:
                with st.spinner(f"Generating answer for {button_name}..."):
                    generate_answer(button_question)

    st.markdown("---")
    st.markdown("### ⚙️ System Status")

    if GEMINI_API_KEY:
        st.success("Gemini API Connected")
    else:
        st.error("Gemini API Missing")

    st.info("FAISS + Sentence Transformers + Gemini")


st.markdown("""
<div class="hero">
    <div class="badge">🚀 RAG Powered University Assistant</div>
    <h1>Ask University Questions<br><span>Get Instant AI Answers</span></h1>
    <p>
        This smart help desk searches university documents using FAISS and generates
        simple answers with Gemini AI. Useful for students asking about fees,
        admission, hostel rules, exams, library, scholarships and placements.
    </p>
</div>
""", unsafe_allow_html=True)

st.write("")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="stat-card">
        <h3>01</h3>
        <p>Student asks question</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-card">
        <h3>02</h3>
        <p>FAISS searches documents</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-card">
        <h3>03</h3>
        <p>Gemini creates answer</p>
    </div>
    """, unsafe_allow_html=True)


st.markdown('<div class="query-card">', unsafe_allow_html=True)

st.markdown('<div class="section-title">💬 Ask Your Question</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Type your question and press Enter, click Generate Answer, or use sidebar topic buttons.</div>',
    unsafe_allow_html=True,
)

example_questions = [
    "What are the hostel rules?",
    "What is the library timing?",
    "Tell me about scholarship details.",
    "What are the placement rules?",
]

selected_example = st.selectbox(
    "Choose sample question",
    [""] + example_questions,
)

if selected_example:
    st.session_state["question"] = selected_example

with st.form("question_form", clear_on_submit=False):
    question = st.text_input(
        "Your Question",
        value=st.session_state["question"],
        placeholder="Example: What are the hostel rules?",
    )

    ask = st.form_submit_button(
        "✨ Generate Answer",
        type="primary",
        use_container_width=True
    )

clear = st.button("Clear Question", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)


if clear:
    st.session_state["question"] = ""
    st.session_state["answer"] = ""
    st.session_state["relevant_chunks"] = []
    st.session_state["last_question"] = ""
    st.rerun()


if ask:
    st.session_state["question"] = question

    if not question.strip():
        st.warning("Please type a question first.")

    elif not GEMINI_API_KEY:
        st.markdown(
            '<div class="error-card">⚠️ GEMINI_API_KEY is missing. Please add it in your .env file.</div>',
            unsafe_allow_html=True,
        )

    else:
        with st.spinner("Searching university documents and generating answer..."):
            generate_answer(question)


if st.session_state["answer"]:
    st.markdown(f"""
    <div class="answer-card">
        <div class="answer-label">AI Answer</div>
        <b>Question:</b> {st.session_state["last_question"]}<br><br>
        {st.session_state["answer"]}
    </div>
    """, unsafe_allow_html=True)

    st.success("Answer generated successfully.")

    with st.expander("📄 View source chunks used by RAG"):
        for i, chunk in enumerate(st.session_state["relevant_chunks"], 1):
            st.markdown(f"### Chunk {i}")
            st.write(chunk)
            st.markdown("---")

    with st.expander("🧠 How this answer was generated"):
        st.markdown("""
        <div class="info-box">
            <b>Step 1:</b> Your question was converted into embeddings.<br>
            <b>Step 2:</b> FAISS searched the most relevant document chunks.<br>
            <b>Step 3:</b> Gemini used only those chunks to generate the answer.<br>
            <b>Step 4:</b> The final answer was shown in simple student-friendly language.
        </div>
        """, unsafe_allow_html=True)