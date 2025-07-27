from document_processor import extract_headings_and_sections
from relevance_model import score_relevance
from llm_engine import generate_refined_texts
from utils import load_input_json, save_output_json
from datetime import datetime

def main():
    input_data = load_input_json("app/input/input.json")
    docs = input_data["documents"]
    persona = input_data["persona"]["role"]
    job = input_data["job_to_be_done"]["task"]
    test_case = input_data["challenge_info"]["test_case_name"]

    all_sections = extract_headings_and_sections(docs)
    ranked = score_relevance(all_sections, persona, job)
    refined = generate_refined_texts(ranked, persona, job)

    output = {
        "metadata": {
            "input_documents": [d["filename"] for d in docs],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": str(datetime.now())
        },
        "extracted_sections": [
            {
                "document": s["document"],
                "section_title": s["section_title"],
                "importance_rank": i+1,
                "page_number": s["page_number"]
            }
            for i, s in enumerate(ranked)
        ],
        "subsection_analysis": refined
    }

    save_output_json(output, test_case)

if __name__ == "__main__":
    main()