from fpdf import FPDF


def create_sample_report(output_filename: str = "report.pdf") -> None:
    """Generate a sample PDF report with student grades."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "2. CS 101 - Intro to Programming: Student Grades", ln=True, align="L")
    pdf.ln(4)

    # Description
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(
        0,
        6,
        "Below is the complete grade roster for CS 101, Section A, taught by Prof. Daniel Okafor. "
        "Grades reflect combined performance on assignments (40%), midterm (25%), and final exam (35%).",
    )
    pdf.ln(6)

    # Table Header
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(220, 230, 242)
    headers = ["Student ID", "Name", "Assign (%)", "Midterm (%)", "Final (%)", "Overall (%)", "Grade"]
    col_widths = [26, 36, 24, 25, 23, 24, 18]

    for header, width in zip(headers, col_widths):
        pdf.cell(width, 8, header, border=1, align="C", fill=True)
    pdf.ln()

    # Table Data
    data = [
        ["WU20212824", "Anderson, Emma", "56.1", "63.8", "61.2", "59.8", "F"],
        ["WU20211188", "Becker, Riley", "85.6", "55.7", "94.2", "81.1", "B"],
        ["WU20212679", "Brooks, Liam", "85.5", "94.6", "54.3", "76.9", "C"],
        ["WU20217912", "Carter, Sophia", "56.4", "54.7", "61.6", "57.8", "F"],
        ["WU20215371", "Costa, Jack", "89.6", "67.0", "64.7", "75.2", "C"],
        ["WU20213591", "Dahl, Zoey", "75.4", "97.7", "93.8", "87.4", "B"],
    ]

    pdf.set_font("Arial", "", 9)
    for row in data:
        for item, width in zip(row, col_widths):
            pdf.cell(width, 7, item, border=1, align="C")
        pdf.ln()

    pdf.output(output_filename)
    print(f"Sample PDF report created: {output_filename}")


if __name__ == "__main__":
    create_sample_report()
