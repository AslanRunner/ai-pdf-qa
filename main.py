"""Main entry point for Multi-PDF Question Answering and Comparison Tool."""

import sys
from config import get_api_key
from pdf_extractor import PDFExtractor
from chat_agent import PDFChatAgent


def print_banner() -> None:
    """Print the application banner."""
    print("=" * 36)
    print("Multi-PDF Question Answering Tool")
    print("=" * 36)
    print()


def run_multi_pdf_qa() -> None:
    """Run the interactive Multi-PDF Q&A and Comparison CLI."""
    print_banner()

    # Step 1: Prompt for PDF directory or file path
    documents = []
    while True:
        target_path = input("Enter the directory containing PDFs: ").strip().strip('"').strip("'")
        if not target_path:
            continue
        if target_path.lower() in ("quit", "exit"):
            print("Goodbye!")
            return

        print("\nLoading PDFs...")
        try:
            documents = PDFExtractor.extract_path(target_path)
            for doc in documents:
                page_label = "page" if doc.page_count == 1 else "pages"
                print(f"✓ Loaded: {doc.file_name} ({doc.page_count} {page_label}, {doc.char_count:,} characters)")

            pdf_count_label = "PDF" if len(documents) == 1 else "PDFs"
            print(f"\n✓ Loaded {len(documents)} {pdf_count_label}")
            print("✓ Ready for questions!\n")
            break
        except FileNotFoundError:
            print(f"Error: Path '{target_path}' not found. Please enter a valid directory.\n")
        except ValueError as e:
            print(f"Error: {e}\n")
        except Exception as e:
            print(f"Error loading PDFs: {e}\n")

    # Step 2: Initialize API and Agent
    api_key = get_api_key()

    try:
        agent = PDFChatAgent(api_key=api_key)
        agent.set_documents(documents)
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
    run_multi_pdf_qa()
