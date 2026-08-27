from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage


class PDFChatAgent:
    """Conversational agent that answers questions based on PDF context."""

    FALLBACK_MODELS = ["gemini-3.6-flash", "gemini-3.6-pro", "gemini-2.5-flash", "gemini-1.5-flash"]

    def __init__(self, api_key: str, model_name: str = "gemini-3.6-flash", temperature: float = 0.2):
        """Initialize LLM and agent state."""
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.llm = self._create_llm(model_name)
        self.messages: list[BaseMessage] = []

    def _create_llm(self, model_name: str) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self.api_key,
            temperature=self.temperature
        )

    def set_document_context(self, content: str) -> None:
        """Initialize the conversation with the document content as system prompt."""
        system_prompt = (
            "You are a helpful assistant that answers questions about this PDF document.\n\n"
            "Document content:\n"
            f"{content}\n\n"
            "Answer based only on the information in this document."
        )
        self.messages = [SystemMessage(content=system_prompt)]

    def ask(self, question: str) -> str:
        """Send a question to the agent, update history, and return the response."""
        self.messages.append(HumanMessage(content=question))

        try:
            response = self.llm.invoke(self.messages)
            self.messages.append(response)
            return str(response.content)
        except Exception as e:
            error_str = str(e)
            # If the specific model is not found or unsupported, try fallback models
            if "not found" in error_str.lower() or "404" in error_str:
                for fallback in self.FALLBACK_MODELS:
                    if fallback != self.model_name:
                        try:
                            print(f"[Bilgi] '{self.model_name}' yerine '{fallback}' modeli deneniyor...")
                            self.llm = self._create_llm(fallback)
                            response = self.llm.invoke(self.messages)
                            self.model_name = fallback
                            self.messages.append(response)
                            return str(response.content)
                        except Exception:
                            continue
            # Remove the last unanswered question from history on failure
            if self.messages and isinstance(self.messages[-1], HumanMessage):
                self.messages.pop()
            raise e

    def reset(self) -> None:
        """Clear conversation history while keeping LLM configuration."""
        self.messages = []

