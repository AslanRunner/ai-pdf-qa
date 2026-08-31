"""Streamlit Web Application for Human-Crafted Multi-PDF Research.

Design Philosophy:
- Antique White & Deep Dark Blue palette with full Light & Dark mode support
- Restrained, authentic human craftsmanship (no AI badges, no robotic telemetry boxes, no cheesy clichés)
- Typography: Newsreader (Editorial Serif) + Source Sans 3 (Body) + IBM Plex Mono (Subtle metadata)
- Powers of two spacing (2, 4, 8, 16, 32, 64, 128)
"""

from pathlib import Path
import streamlit as st
from config import get_api_key
from pdf_extractor import PDFExtractor, PDFDocument
from chat_agent import PDFChatAgent

# -----------------------------------------------------------------------------
# 1. PAGE SETUP
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Folio · Belge Araştırma",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. SESSION STATE
# -----------------------------------------------------------------------------
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "light"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "documents" not in st.session_state:
    st.session_state.documents = []

if "agent" not in st.session_state:
    st.session_state.agent = None

if "processed" not in st.session_state:
    st.session_state.processed = False

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemini-3.6-flash"

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.2

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# -----------------------------------------------------------------------------
# 3. DYNAMIC STYLES (LIGHT / DARK THEME IN ANTIQUE WHITE & DARK BLUE)
# -----------------------------------------------------------------------------
is_dark = st.session_state.theme_mode == "dark"

THEME_VARS = """
    --bg-canvas: #09121f;
    --bg-surface: #101d2f;
    --bg-surface-hover: #16273e;
    --bg-subtle: #17253a;
    --text-main: #f5eee3;
    --text-secondary: #c7d2e0;
    --text-muted: #8899ac;
    --border-color: #1f334d;
    --border-strong: #2d4566;
    --accent-brand: #d8a65c;
    --accent-brand-hover: #e6b872;
    --accent-blue: #72a4db;
    --bubble-user: #16273e;
    --bubble-user-border: #263e5e;
    --bubble-ai: #101d2f;
    --bubble-ai-border: #1f334d;
    --code-bg: #0b1524;
    --shadow-soft: 0 4px 20px rgba(0, 0, 0, 0.4);
""" if is_dark else """
    --bg-canvas: #faf6ef;
    --bg-surface: #ffffff;
    --bg-surface-hover: #fdfbf7;
    --bg-subtle: #f3ebe0;
    --text-main: #0c1b33;
    --text-secondary: #3b495c;
    --text-muted: #6e7d91;
    --border-color: #e4dac8;
    --border-strong: #c8bba4;
    --accent-brand: #0c1b33;
    --accent-brand-hover: #162b4e;
    --accent-blue: #1c3d6e;
    --bubble-user: #f3ede2;
    --bubble-user-border: #ded2be;
    --bubble-ai: #ffffff;
    --bubble-ai-border: #e4dac8;
    --code-bg: #f4ecdf;
    --shadow-soft: 0 4px 20px rgba(12, 27, 51, 0.05);
"""

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;0,6..72,700;0,6..72,800;1,6..72,400;1,6..72,600&family=Source+Sans+3:ital,wght@0,400;0,500;0,600;1,400&display=swap');

:root {{
    {THEME_VARS}
    --space-2: 2px;
    --space-4: 4px;
    --space-8: 8px;
    --space-16: 16px;
    --space-32: 32px;
    --space-64: 64px;
}}

/* Global resets */
.stApp {{
    background-color: var(--bg-canvas);
    font-family: 'Source Sans 3', sans-serif;
    color: var(--text-main);
    transition: background-color 0.25s ease, color 0.25s ease;
}}

/* Main container sizing */
.main .block-container {
    max-width: 860px;
    padding-top: var(--space-24, 24px);
    padding-bottom: var(--space-64);
    margin: 0 auto;
}

/* Sidebar styling - clearly distinguished */
section[data-testid="stSidebar"] {
    background-color: var(--bg-surface);
    border-right: 1px solid var(--border-color);
    box-shadow: 2px 0 12px rgba(0, 0, 0, 0.03);
}

section[data-testid="stSidebar"] .block-container {
    padding-top: var(--space-32);
    padding-bottom: var(--space-32);
}

/* Top Navigation Masthead */
.masthead {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: var(--space-8);
    padding-bottom: var(--space-16);
    border-bottom: 1px solid var(--border-color);
    margin-bottom: var(--space-32);
}}

.masthead-brand {{
    display: flex;
    align-items: baseline;
    gap: var(--space-8);
}}

.masthead-logo {{
    font-family: 'Newsreader', Georgia, serif;
    font-weight: 800;
    font-size: 1.85rem;
    letter-spacing: -0.03em;
    color: var(--text-main);
    text-decoration: none;
}}

.masthead-subtitle {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-muted);
    letter-spacing: 0.05em;
}}

/* Hero section */
.hero-box {{
    margin-bottom: var(--space-32);
}}

.hero-heading {{
    font-family: 'Newsreader', Georgia, serif;
    font-weight: 700;
    font-size: 2.5rem;
    line-height: 1.15;
    letter-spacing: -0.02em;
    color: var(--text-main);
    margin: 0 0 var(--space-8) 0;
}}

.hero-subtext {{
    font-size: 1.08rem;
    line-height: 1.55;
    color: var(--text-secondary);
    max-width: 620px;
    margin: 0;
}}

/* Document Bar (when documents are active) */
.doc-bar {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-8);
    padding: var(--space-12, 12px) var(--space-16);
    background-color: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--space-4);
    margin-bottom: var(--space-24, 24px);
    box-shadow: var(--shadow-soft);
}}

.doc-chip {{
    display: inline-flex;
    align-items: center;
    gap: var(--space-4);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.76rem;
    background-color: var(--bg-subtle);
    color: var(--text-main);
    padding: var(--space-4) var(--space-8);
    border: 1px solid var(--border-color);
    border-radius: var(--space-2);
}}

/* Button styling */
div.stButton > button {{
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.88rem;
    font-weight: 600;
    background-color: var(--bg-surface);
    color: var(--text-main);
    border: 1px solid var(--border-strong);
    border-radius: var(--space-4);
    padding: var(--space-8) var(--space-16);
    transition: all 0.15s ease;
}}

div.stButton > button:hover {{
    background-color: var(--accent-brand);
    color: {'#09121f' if is_dark else '#ffffff'};
    border-color: var(--accent-brand);
}}

div.stButton > button[kind="primary"] {{
    background-color: var(--accent-brand);
    color: {'#09121f' if is_dark else '#ffffff'};
    border-color: var(--accent-brand);
}}

div.stButton > button[kind="primary"]:hover {{
    background-color: var(--accent-brand-hover);
    border-color: var(--accent-brand-hover);
}}

/* Chat messages */
div.stChatMessage {{
    background-color: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--space-4);
    padding: var(--space-16);
    margin-bottom: var(--space-16);
    color: var(--text-main);
    box-shadow: var(--shadow-soft);
}}

div.stChatMessage[data-testid="stChatMessageUser"] {{
    background-color: var(--bubble-user);
    border-color: var(--bubble-user-border);
}}

div.stChatMessage[data-testid="stChatMessageAssistant"] {{
    background-color: var(--bubble-ai);
    border-color: var(--bubble-ai-border);
}}

div.stChatMessage h1, div.stChatMessage h2, div.stChatMessage h3 {{
    font-family: 'Newsreader', Georgia, serif;
    font-weight: 700;
    color: var(--text-main);
    margin-top: var(--space-16);
    margin-bottom: var(--space-8);
}}

div.stChatMessage code {{
    font-family: 'IBM Plex Mono', monospace;
    background-color: var(--code-bg);
    color: var(--text-main);
    padding: var(--space-2) var(--space-4);
    border-radius: var(--space-2);
    border: 1px solid var(--border-color);
    font-size: 0.88em;
}}

/* Chat input bar */
div[data-testid="stChatInput"] {{
    background-color: var(--bg-surface);
    border: 1px solid var(--border-strong);
    border-radius: var(--space-4);
    box-shadow: var(--shadow-soft);
}}

div[data-testid="stChatInput"] textarea {{
    color: var(--text-main) !important;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.95rem;
}}

/* File uploader */
div[data-testid="stFileUploader"] section {{
    background-color: var(--bg-surface);
    border: 1px dashed var(--border-strong);
    border-radius: var(--space-4);
    padding: var(--space-16);
}}

/* Minimalist empty box */
.empty-box {{
    background-color: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--space-4);
    padding: var(--space-32);
    text-align: center;
    box-shadow: var(--shadow-soft);
    margin-top: var(--space-16);
    margin-bottom: var(--space-32);
}}

.empty-box h3 {{
    font-family: 'Newsreader', Georgia, serif;
    font-weight: 700;
    font-size: 1.5rem;
    margin-bottom: var(--space-8);
    color: var(--text-main);
}}

.empty-box p {{
    color: var(--text-secondary);
    font-size: 0.95rem;
    max-width: 460px;
    margin: 0 auto var(--space-24, 24px) auto;
}}

/* Suggestion pills */
.suggestion-header {{
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: var(--space-8);
}}

/* Simple footer */
.simple-footer {{
    margin-top: var(--space-64);
    padding-top: var(--space-16);
    padding-bottom: var(--space-16);
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-muted);
}}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 4. UTILITIES
# -----------------------------------------------------------------------------
def clean_text_for_display(text: str) -> str:
    """Ensure text is clean markdown."""
    trimmed = text.strip()
    if (trimmed.startswith("[{'type':") or trimmed.startswith('[{"type":')) and "text" in trimmed:
        try:
            import ast
            parsed = ast.literal_eval(trimmed)
            if isinstance(parsed, list):
                parts = [p.get("text", "") for p in parsed if isinstance(p, dict) and "text" in p]
                if parts:
                    return "\n\n".join(parts).strip()
        except Exception:
            pass
    return text


def load_local_samples() -> list[PDFDocument]:
    """Load sample report PDFs from local documents folder."""
    sample_dir = Path(__file__).resolve().parent / "documents"
    sample_docs = []
    if sample_dir.exists():
        for p in sorted(sample_dir.glob("*.pdf")):
            try:
                doc = PDFExtractor.extract_file(p)
                sample_docs.append(doc)
            except Exception as exc:
                st.sidebar.error(f"Sample load error ({p.name}): {exc}")
    return sample_docs


# -----------------------------------------------------------------------------
# 5. TOP MASTHEAD & THEME SWITCHER
# -----------------------------------------------------------------------------
col_brand, col_theme = st.columns([3, 1])
with col_brand:
    st.markdown(
        """
        <div class="masthead-brand">
            <span class="masthead-logo">Folio</span>
            <span class="masthead-subtitle">/ Belge Araştırma</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_theme:
    # Human-friendly theme switch
    theme_selected = st.radio(
        "Tema",
        ["Açık", "Koyu"],
        horizontal=True,
        index=1 if is_dark else 0,
        label_visibility="collapsed",
    )
    new_mode = "dark" if theme_selected == "Koyu" else "light"
    if new_mode != st.session_state.theme_mode:
        st.session_state.theme_mode = new_mode
        st.rerun()

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. SIDEBAR (DOCUMENTS & SETTINGS)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📁 Belgeler")
    uploaded_files = st.file_uploader(
        "PDF Dosyaları",
        type=["pdf"],
        accept_multiple_files=True,
        help="Analiz etmek istediğiniz PDF'leri buraya yükleyin.",
    )

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        process_clicked = st.button("Yükle & İncele", type="primary", use_container_width=True)
    with col_s2:
        sample_clicked = st.button("Örnekleri Aç", use_container_width=True)

    if process_clicked:
        if not uploaded_files:
            st.warning("Lütfen en az bir dosya seçin.")
        else:
            with st.spinner("Belgeler okunuyor..."):
                docs: list[PDFDocument] = []
                for f in uploaded_files:
                    try:
                        doc = PDFExtractor.extract_stream(f, file_name=f.name)
                        docs.append(doc)
                    except Exception as e:
                        st.error(f"Hata ({f.name}): {e}")

                if docs:
                    api_key = get_api_key()
                    agent = PDFChatAgent(
                        api_key=api_key,
                        model_name=st.session_state.selected_model,
                        temperature=st.session_state.temperature,
                    )
                    agent.set_documents(docs)
                    st.session_state.documents = docs
                    st.session_state.agent = agent
                    st.session_state.processed = True
                    st.session_state.messages = []
                    st.rerun()

    if sample_clicked:
        with st.spinner("Örnek belgeler açılıyor..."):
            sample_docs = load_local_samples()
            if sample_docs:
                api_key = get_api_key()
                agent = PDFChatAgent(
                    api_key=api_key,
                    model_name=st.session_state.selected_model,
                    temperature=st.session_state.temperature,
                )
                agent.set_documents(sample_docs)
                st.session_state.documents = sample_docs
                st.session_state.agent = agent
                st.session_state.processed = True
                st.session_state.messages = []
                st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Ayarlar")
    available_models = ["gemini-3.6-flash", "gemini-3.6-pro", "gemini-2.5-flash", "gemini-1.5-flash"]
    chosen_model = st.selectbox(
        "Model",
        available_models,
        index=available_models.index(st.session_state.selected_model) if st.session_state.selected_model in available_models else 0,
    )
    if chosen_model != st.session_state.selected_model:
        st.session_state.selected_model = chosen_model
        if st.session_state.agent and st.session_state.documents:
            st.session_state.agent = PDFChatAgent(
                api_key=get_api_key(),
                model_name=chosen_model,
                temperature=st.session_state.temperature,
            )
            st.session_state.agent.set_documents(st.session_state.documents)

    chosen_temp = st.slider(
        "Yaratıcılık Derecesi",
        min_value=0.0,
        max_value=1.0,
        value=float(st.session_state.temperature),
        step=0.05,
    )
    if chosen_temp != st.session_state.temperature:
        st.session_state.temperature = chosen_temp
        if st.session_state.agent and st.session_state.documents:
            st.session_state.agent.temperature = chosen_temp
            st.session_state.agent.llm = st.session_state.agent._create_llm(st.session_state.selected_model)

    if st.session_state.processed and st.session_state.documents:
        st.markdown("---")
        if st.button("Sohbeti Temizle", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.agent:
                st.session_state.agent.reset()
                st.session_state.agent.set_documents(st.session_state.documents)
            st.rerun()

# -----------------------------------------------------------------------------
# 7. MAIN WORKBENCH
# -----------------------------------------------------------------------------
if not st.session_state.processed:
    st.markdown(
        """
        <div class="hero-box">
            <h1 class="hero-heading">Belgelerinizi derinlemesine okuyun ve karşılaştırın.</h1>
            <p class="hero-subtext">
                PDF formatındaki araştırma raporlarını, ders notlarını veya sözleşmeleri yükleyin; sorularınızı doğrudan metne dayalı olarak yanıtlayalım.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="empty-box">
            <h3>Başlamak için belge yükleyin</h3>
            <p>Sol panelden kendi PDF dosyalarınızı ekleyin veya mevcut iki örnek raporu tek tıkla deneyin.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        if st.button("Örnek Raporları Yükle (2 PDF)", type="primary", use_container_width=True):
            sample_docs = load_local_samples()
            if sample_docs:
                api_key = get_api_key()
                agent = PDFChatAgent(
                    api_key=api_key,
                    model_name=st.session_state.selected_model,
                    temperature=st.session_state.temperature,
                )
                agent.set_documents(sample_docs)
                st.session_state.documents = sample_docs
                st.session_state.agent = agent
                st.session_state.processed = True
                st.session_state.messages = []
                st.rerun()

else:
    # Active document status bar
    doc_chips_html = "".join(
        f'<span class="doc-chip">📄 {doc.file_name} <small>({doc.page_count} sayfa)</small></span>'
        for doc in st.session_state.documents
    )
    st.markdown(
        f"""
        <div class="doc-bar">
            <span style="font-size: 0.85rem; font-weight: 600; margin-right: 4px;">Aktif Belgeler:</span>
            {doc_chips_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # If no messages yet, show subtle suggestion chips
    if not st.session_state.messages:
        st.markdown('<div class="suggestion-header">Örnek İpuçları</div>', unsafe_allow_html=True)
        col_q1, col_q2, col_q3 = st.columns(3)
        with col_q1:
            if st.button("📌 Belgelerin ana fikrini özetle", use_container_width=True):
                st.session_state.pending_prompt = "Yüklenen belgelerin ana konusunu ve önemli sonuçlarını özetle."
        with col_q2:
            if st.button("⚖️ Belgeleri tabloyla karşılaştır", use_container_width=True):
                st.session_state.pending_prompt = "Belgeleri temel kriterler, yöntemler ve bulgular açısından karşılaştıran bir tablo hazırla."
        with col_q3:
            if st.button("🔍 Sayısal verileri listele", use_container_width=True):
                st.session_state.pending_prompt = "Belgelerdeki tüm sayısal verileri, istatistikleri ve yüzdeleri çıkar."

    # Render Conversation History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(clean_text_for_display(message["content"]))

    # Prompt Input
    prompt = st.chat_input("Belgelerle ilgili bir soru sorun...")
    if st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Belgeler inceleniyor..."):
                try:
                    response = st.session_state.agent.ask(prompt)
                    clean_response = clean_text_for_display(response)
                    st.markdown(clean_response)
                    st.session_state.messages.append({"role": "assistant", "content": clean_response})
                except Exception as e:
                    st.error(f"Bir hata oluştu: {e}")

