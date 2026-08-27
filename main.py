import sys
from config import get_api_key
from pdf_extractor import PDFExtractor
from chat_agent import PDFChatAgent


def print_banner() -> None:
    """Print the application banner."""
    print("=" * 29)
    print("PDF Question Answering Tool")
    print("=" * 29)
    print()


def run_pdf_qa() -> None:
    """Run the interactive PDF Q&A command line loop."""
    print_banner()

    # Step 1: Prompt for PDF file path
    while True:
        pdf_path = input("Enter the path to your PDF file: ").strip().strip('"').strip("'")
        if not pdf_path:
            continue
        if pdf_path.lower() in ("quit", "exit"):
            print("Goodbye!")
            return

        print("\nLoading PDF...")
        try:
            doc = PDFExtractor.extract(pdf_path)
            print(f"✓ Loaded: {doc.file_path}")
            print(f"  Pages: {doc.page_count}")
            print(f"  Characters: {doc.char_count:,}")
            print("✓ Ready for questions!\n")
            break
        except FileNotFoundError:
            print(f"Error: File '{pdf_path}' not found. Please enter a valid path.\n")
        except Exception as e:
            print(f"Error loading PDF: {e}\n")

    # Step 2: Initialize API and Agent
    api_key = get_api_key()

    try:
        agent = PDFChatAgent(api_key=api_key)
        agent.set_document_context(doc.content)
    except Exception as e:
        print(f"Failed to initialize AI Agent: {e}")
        sys.exit(1)

    # Step 3: Interactive Q&A loop
    while True:
        try:
            question = input("Ask a question (or 'quit' to exit): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not question:
            continue

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        print("\nThinking...")
        try:
            answer = agent.ask(question)
            print(f"\nAnswer:\n{answer}\n")
        except Exception as e:
            print(f"\nError generating answer: {e}\n")


if __name__ == "__main__":
    run_pdf_qa()
