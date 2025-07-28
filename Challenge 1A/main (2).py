#!/usr/bin/env python3
"""
Challenge 1B – Multi-Collection PDF Analysis
-------------------------------------------
• Reads every sub-folder of /app/input that contains `challenge1b_input.json`
• For each collection:
    1. Builds a relevance query from persona + job-to-be-done
    2. Parses each PDF page with pdfminer.six
    3. Scores pages via TF-IDF cosine similarity to the query
    4. Emits `challenge1b_output.json` with:
        - metadata
        - extracted_sections   (top-k pages, ranked)
        - subsection_analysis  (key snippet from each page)
"""

import json, re, sys, math, traceback
from pathlib import Path
from typing import List, Dict

from pdfminer.high_level import extract_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------- helper -------------------------------------------------------- #
def load_pages(pdf_path: Path) -> List[str]:
    """Return list of page-level texts (index = page-1)."""
    try:
        text = extract_text(str(pdf_path))  # full doc, page-delimited
        # pdfminer separates pages with \x0c (form feed)
        return [p.strip() for p in text.split("\f") if p.strip()]
    except Exception as e:
        print(f"[ERROR] {pdf_path.name}: {e}")
        traceback.print_exc()
        return []


def page_title(page_text: str) -> str:
    """Pick a naive 'section title': first non-blank line ≤ 80 chars."""
    for line in page_text.splitlines():
        line = line.strip()
        if 0 < len(line) <= 80:
            return line
    return "Untitled Section"


def snippet(text: str, limit: int = 280) -> str:
    """Take the first ~limit chars, stop at last full sentence if possible."""
    if len(text) <= limit:
        return text
    cut = text[:limit]
    # try to cut at last period
    idx = cut.rfind(". ")
    return cut[: idx + 1] if idx != -1 else cut + "…"


# ---------- core ---------------------------------------------------------- #
def analyse_collection(folder: Path):
    cfg_path = folder / "challenge1b_input.json"
    with cfg_path.open() as f:
        cfg = json.load(f)

    persona = cfg["persona"]["role"]
    task    = cfg["job_to_be_done"]["task"]
    query   = f"{persona}. {task}"

    pdf_dir = folder / "PDFs"
    pdf_files = list(pdf_dir.glob("*.pdf"))

    pages_meta = []  # list[dict] for scoring

    for pdf in pdf_files:
        for idx, page_text in enumerate(load_pages(pdf), start=1):
            pages_meta.append({
                "document": pdf.name,
                "page_number": idx,
                "text": page_text
            })

    if not pages_meta:
        print(f"[WARN] No text extracted in {folder.name}")
        return

    # TF-IDF vectorisation -------------------------------------------------
    corpus    = [p["text"] for p in pages_meta] + [query]
    vectorizer = TfidfVectorizer(stop_words="english", max_df=0.9)
    tfidf      = vectorizer.fit_transform(corpus)
    sims       = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()  # query vs pages

    # attach similarity
    for meta, score in zip(pages_meta, sims):
        meta["score"] = float(score)

    # rank pages by similarity
    pages_meta.sort(key=lambda d: d["score"], reverse=True)
    top_pages = pages_meta[: min(5, len(pages_meta))]

    # build output ---------------------------------------------------------
    extracted_sections = []
    subsection_analysis = []

    for rank, page in enumerate(top_pages, start=1):
        extracted_sections.append({
            "document": page["document"],
            "section_title": page_title(page["text"]),
            "importance_rank": rank,
            "page_number": page["page_number"]
        })
        subsection_analysis.append({
            "document": page["document"],
            "refined_text": snippet(page["text"]),
            "page_number": page["page_number"]
        })

    output = {
        "metadata": {
            "input_documents": [p.name for p in pdf_files],
            "persona": persona,
            "job_to_be_done": task
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    out_path = folder / "challenge1b_output.json"
    json.dump(output, out_path.open("w"), indent=2, ensure_ascii=False)
    print(f"[DONE] {folder.name} → {out_path.name}")


def main(root: str = "/app/input"):
    root_path = Path(root)
    for coll in root_path.iterdir():
        if (coll / "challenge1b_input.json").exists():
            print(f"[INFO] Analysing {coll.name}")
            analyse_collection(coll)


if __name__ == "__main__":
    main(*(sys.argv[1:] or []))
