"""LangChain Gemini Chat Agent module for single and multi-PDF question answering."""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from pdf_extractor import PDFDocument


class PDFChatAgent:
    """Conversational agent that analyzes and compares PDF documents."""

    FALLBACK_MODELS = ["gemini-3.6-flash", "gemini-3.6-pro", "gemini-2.5-flash", "gemini-1.5-flash"]

    def __init__(self, api_key: str, model_name: str = "gemini-3.6-flash", temperature: float | None = None):
        """Initialize LLM and agent state."""
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.llm = self._create_llm(model_name)
        self.messages: list[BaseMessage] = []

    def _create_llm(self, model_name: str) -> ChatGoogleGenerativeAI:
        kwargs = {
            "model": model_name,
            "google_api_key": self.api_key,
        }
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature
        return ChatGoogleGenerativeAI(**kwargs)

    def set_documents(self, documents: list[PDFDocument]) -> None:
        """Initialize conversation with labeled content from multiple PDF documents."""
        combined_context = []
        for doc in documents:
            combined_context.append(f"=== {doc.file_name} ===\n{doc.content}")

        context_str = "\n\n".join(combined_context)

        system_prompt = (
            "You are an expert, articulate AI assistant specialized in analyzing and presenting information from PDF documents in a clear, human-friendly manner.\n\n"
            "Here are the loaded documents:\n\n"
            f"{context_str}\n\n"
            "Core Guidelines:\n"
            "1. Base your answers strictly and accurately on the provided documents.\n"
            "2. Always reply in the exact language the user asks their question in.\n"
            "3. State which document information comes from when relevant.\n"
            "4. Presentation Style (Crucial for User Experience):\n"
            "   - Write naturally and fluently. NEVER use mechanical, repetitive form labels like 'Purpose / Definition:' or 'Key Features / Outputs:'.\n"
            "   - Start with a brief, helpful 1-2 sentence introduction or a quick summary table when listing multiple items.\n"
            "   - Present each item (project, paper, experience) as an engaging, well-structured section:\n"
            "     ### 1. Project Name\n"
            "     A fluent, natural 1-2 sentence description explaining what the project is and what problem it solves.\n"
            "     - **Technologies:** `Tech1` · `Tech2` · `Tech3`\n"
            "     - **Highlights:** 1-2 concise bullet points highlighting key algorithms, metrics, or technical accomplishments.\n"
            "   - When comparing multiple documents, prefer clear Markdown comparison tables.\n"
            "   - Use bolding, spacing, and backticks effectively so the response looks clean, elegant, and effortless to read."
        )
        self.messages = [SystemMessage(content=system_prompt)]

    def set_document_context(self, content: str) -> None:
        """Single document context helper for backward compatibility."""
        system_prompt = (
            "You are an expert, articulate AI assistant specialized in analyzing PDF documents in a clear, human-friendly manner.\n\n"
            "Document content:\n"
            f"{content}\n\n"
            "Core Guidelines:\n"
            "1. Answer based strictly on the provided document.\n"
            "2. Always reply in the user's language.\n"
            "3. Write naturally and fluently without mechanical form labels.\n"
            "4. Use clear headings, technology tags (`Tech`), and concise bullet points."
        )
        self.messages = [SystemMessage(content=system_prompt)]

    @staticmethod
    def _extract_text(content: object) -> str:
        """Extract clean plain text from LangChain message content, removing raw metadata/extras dicts."""
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts = []
            for part in content:
                if isinstance(part, str):
                    parts.append(part)
                elif isinstance(part, dict) and "text" in part:
                    parts.append(str(part["text"]))
                elif hasattr(part, "text"):
                    parts.append(str(part.text))
            return "\n".join(parts).strip()
        if hasattr(content, "text"):
            return str(content.text).strip()
        return str(content).strip()

    def ask(self, question: str) -> str:
        """Send a question to the agent, update history, and return the response."""
        self.messages.append(HumanMessage(content=question))

        try:
            response = self.llm.invoke(self.messages)
            self.messages.append(response)
            return self._extract_text(response.content)
        except Exception as e:
            error_str = str(e)
            if "not found" in error_str.lower() or "404" in error_str:
                for fallback in self.FALLBACK_MODELS:
                    if fallback != self.model_name:
                        try:
                            self.llm = self._create_llm(fallback)
                            response = self.llm.invoke(self.messages)
                            self.model_name = fallback
                            self.messages.append(response)
                            return self._extract_text(response.content)
                        except Exception:
                            continue
            if self.messages and isinstance(self.messages[-1], HumanMessage):
                self.messages.pop()
            raise e

    def reset(self) -> None:
        """Clear conversation history while keeping LLM configuration."""
        self.messages = []
