import streamlit as st
import google.generativeai as genai
import pdfplumber
import docx

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄")
st.title("📄 AI Resume Analyzer")
st.write("Upload your resume and get instant AI-powered feedback.")

# --- API Key setup ---
api_key = st.text_input("Enter your Gemini API Key", type="password")

# --- Role input ---
role = st.text_input("Target Role (e.g. AI/ML Intern, Software Engineer)")

# --- File upload ---
uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])


def extract_text(file):
    if file.name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    return ""


if st.button("Analyze Resume"):
    if not api_key:
        st.error("Please enter your Gemini API key.")
    elif not uploaded_file:
        st.error("Please upload a resume file.")
    elif not role:
        st.error("Please enter a target role.")
    else:
        with st.spinner("Reading your resume..."):
            resume_text = extract_text(uploaded_file)

        if not resume_text.strip():
            st.error("Couldn't extract text from this file. Try another format.")
        else:
            with st.spinner("Analyzing with Gemini..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-3.5-flash")
                prompt = f"""
                You are an expert technical recruiter reviewing a resume for a {role} position.

                Resume:
                {resume_text}

                Give feedback in this exact structure:
                1. Overall Score (out of 10)
                2. Top 3 Strengths
                3. Top 3 Weaknesses
                4. 5 Specific, Actionable Improvements
                5. Missing Keywords/Skills for this role
                """

                response = model.generate_content(prompt)

            st.success("Analysis complete!")
            st.markdown(response.text)
