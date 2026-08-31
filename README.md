# AI PDF Q&A and Comparison (ai-pdf-qa)

> A modular application that extracts text from single or multiple PDF documents and provides conversational question answering, cross-document comparison, and synthesis using **Google Gemini** and **LangChain**, available via both **CLI** and a **Streamlit Web UI**.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-Integration-brightgreen.svg)](https://github.com/langchain-ai/langchain)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-Powered-orange.svg)](https://aistudio.google.com/)


---

## Features

- **Modern Web Interface (Streamlit)**: Drag-and-drop PDF upload, document badge overview, and responsive real-time chat interface.
- **Multi-Document Ingestion**: Loads one or many PDF files simultaneously and extracts text directly from memory or disk using `pypdf`.
- **Document Labeling & Context Fusion**: Injects each document's text with explicit file markers (`=== filename ===`) into Gemini's system prompt.
- **Comparative Analysis**: Compares, contrasts, and synthesizes data across multiple documents.
- **Source Attribution**: Accurately cites which PDF document contains specific findings.
- **Conversational Memory**: Retains multi-turn conversation history for natural follow-up queries.
- **Dual Mode Support**: Run as an interactive command-line tool (`main.py`) or as a web app (`app.py`).

---

## Project Structure

```text
ai-pdf-qa/
├── config.py           # Environment variables and API key management
├── pdf_extractor.py    # Single, multi-PDF, directory and stream text extraction
├── chat_agent.py       # LangChain Gemini multi-document agent
├── app.py              # Streamlit Web GUI application
├── main.py             # CLI entry point for command-line usage
├── sample_report.py    # Generates sample comparison reports
├── documents/          # Sample PDF directory for testing
│   ├── report.pdf      # CS 101 course grade roster
│   └── report2.pdf     # DS 201 course grade roster
├── requirements.txt    # Project dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules
└── README.md           # Project documentation
```

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/AslanRunner/ai-pdf-qa.git
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
Add your **Google Gemini API Key** (available for free at [Google AI Studio](https://aistudio.google.com/)):
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## Running the Web App

Launch the web GUI in your browser:
```bash
streamlit run app.py
```

The application will open automatically at `http://localhost:8501`.

1. Upload one or multiple PDF documents using the sidebar.
2. Click **Process PDFs**.
3. Ask questions and compare documents directly in the chat interface.

---

## Running the Command-Line Tool 

Run via terminal:
```bash
python main.py
```

### Example CLI Session

```text
====================================
Multi-PDF Question Answering Tool
====================================

Enter the directory containing PDFs: documents

Loading PDFs...
✓ Loaded: report.pdf (1 page, 792 characters)
✓ Loaded: report2.pdf (1 page, 652 characters)

✓ Loaded 2 PDFs
✓ Ready for questions!

Ask a question (or 'quit' to exit): give me the list of students that are in both pdfs

Thinking...

Answer:
Based on the grade rosters provided in both documents (**report.pdf** and **report2.pdf**), the following students are enrolled in both courses:

1. **Emma Anderson** (CS 101 in report.pdf, DS 201 in report2.pdf)
2. **Sophia Carter** (CS 101 in report.pdf, DS 201 in report2.pdf)
3. **Olivia Evans** (CS 101 in report.pdf, DS 201 in report2.pdf)
4. **Ava Gomez** (CS 101 in report.pdf, DS 201 in report2.pdf)
5. **Mia Ibrahim** (CS 101 in report.pdf, DS 201 in report2.pdf)
6. **Isabella Kim** (CS 101 in report.pdf, DS 201 in report2.pdf)

Ask a question (or 'quit' to exit): quit
Goodbye!
```

---

## Generating Sample Data

To generate sample test documents (`documents/report.pdf` and `documents/report2.pdf`):
```bash
python sample_report.py
```


