"""Utility script to generate sample multi-PDF reports in documents/ folder."""

from pathlib import Path
from fpdf import FPDF


def generate_pdf_table(filename: Path, title: str, description: str, headers: list[str], col_widths: list[int], data: list[list[str]]) -> None:
    """Helper to generate a clean PDF table report."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="L")
    pdf.ln(3)

    # Description
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, description)
    pdf.ln(5)

    # Table Header
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(220, 230, 242)
    for header, width in zip(headers, col_widths):
        pdf.cell(width, 8, header, border=1, align="C", fill=True)
    pdf.ln()

    # Table Data
    pdf.set_font("Arial", "", 9)
    for row in data:
        for item, width in zip(row, col_widths):
            pdf.cell(width, 7, item, border=1, align="C")
        pdf.ln()

    filename.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(filename))
    print(f"Generated: {filename}")


def create_sample_reports() -> None:
    """Generate sample CS 101 and DS 201 reports in documents/ folder."""
    docs_dir = Path("documents")
    docs_dir.mkdir(exist_ok=True)

    headers = ["Student ID", "Name", "Assign (%)", "Midterm (%)", "Final (%)", "Overall (%)", "Grade"]
    col_widths = [26, 36, 24, 25, 23, 24, 18]

    # 1. CS 101 Report (report.pdf)
    cs101_data = [
        ["WU20212824", "Anderson, Emma", "88.5", "92.0", "90.4", "90.1", "A"],
        ["WU20211188", "Becker, Riley", "85.6", "55.7", "94.2", "81.1", "B"],
        ["WU20212679", "Brooks, Liam", "85.5", "94.6", "54.3", "76.9", "C"],
        ["WU20217912", "Carter, Sophia", "78.4", "84.7", "81.6", "81.2", "B"],
        ["WU20215371", "Costa, Jack", "89.6", "67.0", "64.7", "75.2", "C"],
        ["WU20213591", "Dahl, Zoey", "75.4", "97.7", "93.8", "87.4", "B"],
        ["WU20218841", "Evans, Olivia", "94.2", "91.5", "89.0", "91.8", "A"],
        ["WU20216732", "Gomez, Ava", "82.0", "85.4", "88.2", "85.1", "B"],
        ["WU20219904", "Ibrahim, Mia", "90.1", "93.4", "95.0", "92.7", "A"],
        ["WU20214419", "Kim, Isabella", "87.3", "89.2", "86.5", "87.7", "B"],
        ["WU20217543", "Wang, Penelope", "92.4", "88.0", "91.5", "90.8", "A"],
    ]
    generate_pdf_table(
        docs_dir / "report.pdf",
        "1. CS 101 - Intro to Programming (Fall 2025)",
        "Complete grade roster for CS 101, Section A, taught by Prof. Daniel Okafor. "
        "Grades reflect combined performance on assignments (40%), midterm (25%), and final exam (35%).",
        headers,
        col_widths,
        cs101_data
    )

    # 2. DS 201 Report (report2.pdf)
    ds201_data = [
        ["WU20212824", "Anderson, Emma", "91.0", "89.5", "94.0", "91.5", "A"],
        ["WU20217912", "Carter, Sophia", "82.5", "79.0", "85.0", "82.3", "B"],
        ["WU20218841", "Evans, Olivia", "96.0", "94.5", "92.0", "94.3", "A"],
        ["WU20216732", "Gomez, Ava", "89.0", "87.0", "90.5", "88.6", "B"],
        ["WU20219904", "Ibrahim, Mia", "93.5", "91.0", "96.0", "93.4", "A"],
        ["WU20214419", "Kim, Isabella", "84.0", "88.5", "89.0", "86.8", "B"],
        ["WU20217543", "Young, Kai", "79.0", "82.0", "80.5", "80.3", "B"],
        ["WU20210055", "Zhang, Lucas", "95.0", "92.0", "94.0", "93.8", "A"],
    ]
    generate_pdf_table(
        docs_dir / "report2.pdf",
        "2. DS 201 - Intro to Data Science (Spring 2026)",
        "Complete grade roster for DS 201, Section B, taught by Prof. Sarah Jenkins. "
        "Grades reflect combined performance on projects (45%), midterm (25%), and final exam (30%).",
        headers,
        col_widths,
        ds201_data
    )


if __name__ == "__main__":
    create_sample_reports()
