from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

prompt = PromptTemplate(
    input_variables=["text", "persona", "job"],
    template="""
You are helping a {persona}. They are working on the following job: {job}

Below is a section of a document. Rewrite or summarize it in a way that captures the most relevant and refined content for that purpose.

SECTION:
{text}

REFINED VERSION:
"""
)

llm = OllamaLLM(model="mistral")
chain = prompt | llm

def generate_refined_texts(sections, persona, job):
    results = []
    for s in sections:
        output = chain.invoke({
            "text": s["text"],
            "persona": persona,
            "job": job
        })
        results.append({
            "document": s["document"],
            "refined_text": output.strip(),
            "page_number": s["page_number"]
        })
    return results