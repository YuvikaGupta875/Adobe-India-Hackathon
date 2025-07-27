import fitz
import re
from pathlib import Path

def extract_headings_and_sections(documents, input_dir="app/input"):
    all_sections = []

    for doc in documents:
        filename = doc["filename"]
        title = doc["title"]
        pdf_path = Path(input_dir) / filename
        doc_fitz = fitz.open(pdf_path)

        for page_num, page in enumerate(doc_fitz, 1):
            blocks = page.get_text("dict")["blocks"]
            max_font_size = max(
                (span["size"] for block in blocks if "lines" in block for line in block["lines"] for span in line["spans"]),
                default=0
            )

            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    line_text = " ".join(span["text"] for span in line["spans"]).strip()
                    font_sizes = [span["size"] for span in line["spans"]]
                    is_heading = (
                        line_text
                        and line_text[0].isalpha()
                        and line_text.isprintable()
                        and max(font_sizes, default=0) >= 0.9 * max_font_size
                        and len(line_text) < 80
                        and line_text == line_text.title()
                    )
                    if is_heading:
                        all_sections.append({
                            "document": filename,
                            "page_number": page_num,
                            "section_title": line_text,
                            "text": extract_section_text(page, line_text)
                        })
    return all_sections

def extract_section_text(page, heading_text, max_chars=1200):
    full_text = page.get_text()
    lines = full_text.splitlines()
    start_idx = next((i for i, line in enumerate(lines) if heading_text.strip() in line.strip()), None)
    if start_idx is None:
        return ""
    content_lines = []
    for line in lines[start_idx+1:]:
        if line.strip() == "" or line.isspace():
            continue
        if line.istitle() and len(line.strip()) < 80:
            break
        content_lines.append(line.strip())
        if sum(len(l) for l in content_lines) > max_chars:
            break
    return " ".join(content_lines).strip()