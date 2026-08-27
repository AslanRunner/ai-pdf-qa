# 📄 AI PDF Q&A (`ai-pdf-qa`)

> An intelligent, modular CLI tool that extracts text from any PDF document and enables multi-turn conversational question answering using **Google Gemini** and **LangChain**.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-Integration-brightgreen.svg)](https://github.com/langchain-ai/langchain)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-Powered-orange.svg)](https://aistudio.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- **⚡ Fast & Direct Text Extraction**: Extracts text across all pages using `pypdf`.
- **🧠 Full Context Ingestion**: Leverages Gemini's massive context window by injecting the whole document into the system prompt.
- **💬 Conversational Memory**: Maintains chat history across questions so you can ask natural follow-ups.
- **🧩 Modular Architecture**: Clean separation between PDF processing, AI agent logic, configuration, and the CLI interface.
- **🛡️ Secure API Key Handling**: Supports `.env` configuration and interactive prompt fallback.

---

## 📁 Project Structure

```text
ai-pdf-qa/
├── config.py           # Environment variables and API key management
├── pdf_extractor.py    # PDF text extraction & document metadata handling
├── chat_agent.py       # LangChain ChatGoogleGenerativeAI & history manager
├── main.py             # Interactive CLI entry point
├── sample_report.py    # Script to generate sample report.pdf for testing
├── report.pdf          # Sample CS 101 grade report PDF
├── requirements.txt    # Required dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules
└── README.md           # Project documentation
```

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-pdf-qa.git
cd ai-pdf-qa
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```
Add your **Google Gemini API Key** (get one for free at [Google AI Studio](https://aistudio.google.com/)):
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

*(Note: If no `.env` file is found, the CLI will safely prompt you for your key on startup.)*

---

## 🖥️ Usage

Run the tool:
```bash
python main.py
```

### 📝 Example Session

```text
=============================
PDF Question Answering Tool
=============================

Enter the path to your PDF file: report.pdf

Loading PDF...
✓ Loaded: report.pdf
  Pages: 1
  Characters: 577
✓ Ready for questions!

Ask a question (or 'quit' to exit): What was the grade of Liam Brooks in the CS 101 course?

Thinking...

Answer:
Liam Brooks received a grade of **C** in the CS 101 course.

Ask a question (or 'quit' to exit): What was his midterm score?

Thinking...

Answer:
Liam Brooks scored **94.6%** on his midterm exam.

Ask a question (or 'quit' to exit): quit
Goodbye!
```

---

## 🧪 Generate Sample PDF

To generate a sample `report.pdf` (CS 101 student grades roster) for testing:
```bash
python sample_report.py
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
