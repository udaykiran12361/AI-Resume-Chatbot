# 🤖 AI Resume Chatbot

An AI-powered Resume Chatbot built using **Google Gemini, LangChain, FAISS, and Streamlit**. Upload a resume in PDF format and ask questions about education, technical skills, projects, and experience.

## 🚀 Live Demo

[Try the AI Resume Chatbot](https://ai-resume-chatbot-mf3micujhpkyk7dvbw65ds.streamlit.app)

## ✨ Features

- 📄 Upload and process PDF resumes
- ✂️ Split resume text into smaller chunks
- 🧠 Generate embeddings using Google Gemini
- 🔎 Retrieve relevant information using FAISS vector search
- 💬 Ask questions about your resume
- 🤖 Generate answers using Gemini AI
- 📚 Display source pages for retrieved information

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini API
- LangChain
- FAISS
- PyPDF
- Python-dotenv

## ⚙️ Run Locally

1. Clone the repository:

   `git clone https://github.com/udaykiran12361/AI-Resume-Chatbot.git`

2. Open the project folder:

   `cd AI-Resume-Chatbot`

3. Create and activate a virtual environment:

   `python -m venv venv`

   Windows PowerShell:

   `.\venv\Scripts\Activate.ps1`

4. Install dependencies:

   `pip install -r requirements.txt`

5. Create a `.env` file in the project root and add your Gemini API key:

   `GOOGLE_API_KEY=your_gemini_api_key`

6. Run the application:

   `streamlit run app.py`

## 🔐 Security

- Never upload your `.env` file or API keys to GitHub.
- Keep credentials in Streamlit Cloud Secrets when deploying.

## 👨‍💻 Author

**Uday Kiran Chowdary**

GitHub: [udaykiran12361](https://github.com/udaykiran12361)