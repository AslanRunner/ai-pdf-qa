"""Personal Second Brain & Obsidian Zettelkasten Synthesizer.

Transforms raw PDF document collections into an interconnected, atomic Obsidian Vault:
1. Literature Notes: Complete document dossier with YAML frontmatter, summary, quotes & [[wikilinks]].
2. Atomic Concept Notes: Standalone modular mental models, algorithms, and concepts with bidirectional links.
3. Map of Content (MOC): Master Index connecting all documents and concepts in the knowledge graph.
"""

import io
import json
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from pdf_extractor import PDFDocument


@dataclass
class VaultNote:
    """Represents a single Markdown note in the Obsidian Vault."""
    filename: str
    folder: str  # e.g., "Literature", "Concepts", ""
    title: str
    content: str
    note_type: str  # "literature", "concept", "moc"

    @property
    def relative_path(self) -> str:
        if self.folder:
            return f"{self.folder}/{self.filename}"
        return self.filename


@dataclass
class VaultPackage:
    """Contains all notes generated for an Obsidian Vault."""
    literature_notes: list[VaultNote] = field(default_factory=list)
    concept_notes: list[VaultNote] = field(default_factory=list)
    index_note: VaultNote | None = None
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

    @property
    def all_notes(self) -> list[VaultNote]:
        notes = list(self.literature_notes) + list(self.concept_notes)
        if self.index_note:
            notes.append(self.index_note)
        return notes


class SecondBrainSynthesizer:
    """Orchestrates LLM calls to distill PDFs into an interconnected Obsidian Vault."""

    def __init__(self, api_key: str, model_name: str = "gemini-3.6-flash", temperature: float = 0.2):
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
        )

    def synthesize_vault(self, documents: list[PDFDocument]) -> VaultPackage:
        """Synthesize an entire Obsidian Vault from the given documents."""
        if not documents:
            return VaultPackage()

        # Step 1: Synthesize Literature Notes for each document
        lit_notes: list[VaultNote] = []
        for doc in documents:
            note = self._generate_literature_note(doc)
            lit_notes.append(note)

        # Step 2: Extract Atomic Concept Notes across the document corpus
        concept_notes = self._generate_atomic_concepts(documents, lit_notes)

        # Step 3: Generate Map of Content (MOC / Index)
        index_note = self._generate_moc(documents, lit_notes, concept_notes)

        return VaultPackage(
            literature_notes=lit_notes,
            concept_notes=concept_notes,
            index_note=index_note,
        )

    def _generate_literature_note(self, doc: PDFDocument) -> VaultNote:
        """Generate an Obsidian Literature Note with YAML frontmatter, summary, quotes, and wikilinks."""
        clean_name = Path(doc.file_name).stem
        sanitized_title = clean_name.replace("_", " ").replace("-", " ").title()

        prompt = f"""You are a personal knowledge management (PKM) expert practicing Zettelkasten in Obsidian.
Analyze the following document and write a comprehensive, professional Literature Note in Markdown.

Document Name: {doc.file_name}
Total Pages: {doc.page_count}
Content Preview:
{doc.content[:16000]}

Follow this exact structure:
1. Complete YAML Frontmatter:
---
title: "{sanitized_title}"
type: literature-note
date_imported: "{datetime.now().strftime('%Y-%m-%d')}"
source_file: "{doc.file_name}"
page_count: {doc.page_count}
tags:
  - literature
  - second-brain
---

2. # {sanitized_title}
   - Brief 2-3 sentence overview of what this document is.

3. ## 🎯 Core Thesis & Objectives
   - 2-3 bullet points defining the primary thesis, problem tackled, or main purpose.

4. ## 💡 Key Concepts & Insights
   - Use Obsidian wikilinks for every conceptual entity: e.g. [[Concept Name]].
   - Summarize core methodologies, findings, or qualifications.

5. ## 📜 Notable Quotes & Excerpts
   - 2-4 verbatim or near-verbatim quotes from the text with contextual takeaways.

6. ## 🔗 Connected Ideas & Questions
   - Mention 3-5 open questions or potential research links using [[Wikilinks]].

Return ONLY the raw Markdown content with no conversational introduction."""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        content = response.content
        if isinstance(content, list):
            content = "\n".join(str(p.get("text", p) if isinstance(p, dict) else p) for p in content)

        filename = f"{clean_name}.md"
        return VaultNote(
            filename=filename,
            folder="Literature",
            title=sanitized_title,
            content=str(content).strip(),
            note_type="literature",
        )

    def _generate_atomic_concepts(self, documents: list[PDFDocument], lit_notes: list[VaultNote]) -> list[VaultNote]:
        """Extract standalone Zettelkasten atomic concept notes from the document corpus."""
        combined_text = "\n\n".join(
            f"=== {doc.file_name} ===\n{doc.content[:10000]}" for doc in documents
        )
        lit_links = ", ".join(f"[[{Path(n.filename).stem}]]" for n in lit_notes)

        prompt = f"""You are an elite Zettelkasten researcher constructing an Obsidian knowledge graph.
Analyze the provided documents and identify 3 to 6 distinct, modular, atomic concepts (theories, frameworks, methods, metrics, or technical skills).

Documents available: {lit_links}
Content:
{combined_text[:24000]}

For each concept, generate a JSON object with:
- "title": Clean concise concept name (e.g. "Retrieval-Augmented Generation" or "Predictive Modeling")
- "filename": Safe filename (e.g. "Retrieval-Augmented Generation.md")
- "content": Full Obsidian Markdown file including:
  1. YAML frontmatter (type: concept, tags: [atomic-note, concept])
  2. # Concept Title
  3. ## 📌 Definition & Core Principle (1-2 clear, self-contained paragraphs)
  4. ## ⚙️ Mechanism & How It Operates
  5. ## 🔍 Practical Application & Significance
  6. ## 🔗 Bi-directional Links (Must reference [[Parent Document]] and other potential [[Concepts]])

Output format: Return ONLY a valid JSON array of objects with keys ["title", "filename", "content"]. No backtick fencing or markdown wrapper outside the JSON array."""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        raw_text = str(response.content).strip()

        # Clean potential markdown JSON blocks
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_text = "\n".join(lines).strip()

        concept_notes = []
        try:
            items = json.loads(raw_text)
            if isinstance(items, list):
                for item in items:
                    title = item.get("title", "Concept")
                    filename = item.get("filename", f"{title}.md")
                    if not filename.endswith(".md"):
                        filename = f"{filename}.md"
                    content = item.get("content", "")
                    concept_notes.append(VaultNote(
                        filename=filename,
                        folder="Concepts",
                        title=title,
                        content=content.strip(),
                        note_type="concept",
                    ))
        except Exception:
            # Fallback if json parsing fails: create at least one synthesized concept note
            concept_notes.append(VaultNote(
                filename="Key Insights and Methodologies.md",
                folder="Concepts",
                title="Key Insights and Methodologies",
                content=f"""---
type: concept
tags:
  - atomic-note
  - synthesis
---

# Key Insights and Methodologies

## 📌 Overview
Synthesized insights from {lit_links}.

## 🔗 Related Notes
{lit_links}
""",
                note_type="concept",
            ))

        return concept_notes

    def _generate_moc(self, documents: list[PDFDocument], lit_notes: list[VaultNote], concept_notes: list[VaultNote]) -> VaultNote:
        """Generate a central Map of Content (MOC / Index) tying all notes together."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        lit_list = "\n".join(
            f"- [[{Path(n.filename).stem}]] — *{n.title}* ({n.folder})"
            for n in lit_notes
        )

        concept_list = "\n".join(
            f"- [[{Path(n.filename).stem}]] — *{n.title}*"
            for n in concept_notes
        )

        content = f"""---
title: "Map of Content · Document Research"
type: moc
created: "{now}"
tags:
  - moc
  - index
  - second-brain
---

# 🗺️ Map of Content (MOC)

> *Generated by Folio Second Brain Synthesizer on {now}*

---

## 📚 Source Literature Dossiers
{lit_list}

---

## 🧩 Atomic Concept Network
{concept_list}

---

## 🕸️ Knowledge Graph Overview
This Map of Content acts as the central router for your Obsidian vault.
- Navigate to any **Literature Note** to inspect verbatim quotes and executive summaries.
- Open **Atomic Concepts** to see how ideas link across multiple documents.
- Open Obsidian's **Graph View** (`Ctrl+G` / `Cmd+G`) to visualize the emergent connections.
"""

        return VaultNote(
            filename="_Index_MOC.md",
            folder="",
            title="Map of Content (Index)",
            content=content.strip(),
            note_type="moc",
        )

    @staticmethod
    def create_vault_zip(vault: VaultPackage) -> bytes:
        """Package the entire vault into an in-memory ZIP archive ready for Obsidian."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for note in vault.all_notes:
                path = note.relative_path
                zf.writestr(path, note.content.encode("utf-8"))
        return buf.getvalue()

    @staticmethod
    def export_to_directory(vault: VaultPackage, target_dir: str | Path) -> list[Path]:
        """Export notes directly into an existing Obsidian Vault directory."""
        base = Path(target_dir).resolve()
        base.mkdir(parents=True, exist_ok=True)

        saved_paths: list[Path] = []
        for note in vault.all_notes:
            if note.folder:
                folder_path = base / note.folder
                folder_path.mkdir(parents=True, exist_ok=True)
                file_path = folder_path / note.filename
            else:
                file_path = base / note.filename

            file_path.write_text(note.content, encoding="utf-8")
            saved_paths.append(file_path)

        return saved_paths

    @staticmethod
    def save_dialogue_session(
        vault_dir: str | Path,
        documents: list[PDFDocument],
        messages: list[dict],
    ) -> Path:
        """Save an interactive Q&A session as an interconnected Obsidian Dialogue note."""
        base = Path(vault_dir).resolve()
        dialogues_dir = base / "Dialogues"
        dialogues_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d_%H%M")
        display_time = now.strftime("%Y-%m-%d %H:%M")

        doc_links = ", ".join(f"[[{Path(d.file_name).stem}]]" for d in documents)
        filename = f"Dialogue_{timestamp_str}.md"
        file_path = dialogues_dir / filename

        convo_lines = []
        user_turn = 1
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "").strip()
            if role == "user":
                convo_lines.append(f"### ❓ Query {user_turn}: {content}\n")
                user_turn += 1
            else:
                convo_lines.append(f"**💡 Folio Synthesis:**\n\n{content}\n\n---")

        body_text = "\n\n".join(convo_lines)

        note_content = f"""---
title: "Research Dialogue · {display_time}"
type: dialogue
date: "{now.strftime('%Y-%m-%d')}"
sources: [{doc_links}]
tags:
  - dialogue
  - q-and-a
  - second-brain
---

# 💬 Research Dialogue Session ({display_time})

> **Referenced Dossiers:** {doc_links}

---

{body_text}
"""
        file_path.write_text(note_content.strip(), encoding="utf-8")
        return file_path
