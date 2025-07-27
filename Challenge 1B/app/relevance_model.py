from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def score_relevance(sections, persona, job):
    combined = [f"{persona} needs to: {job}"] + [s["text"] for s in sections]
    tfidf = TfidfVectorizer(stop_words="english").fit_transform(combined)
    scores = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
    ranked = sorted(
        zip(sections, scores),
        key=lambda x: x[1],
        reverse=True
    )
    return [
        {
            "document": r[0]["document"],
            "section_title": r[0]["section_title"],
            "page_number": r[0]["page_number"],
            "text": r[0]["text"]
        }
        for r in ranked[:5]
    ]