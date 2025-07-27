def detect_headings(blocks, size_threshold=1.5):
    if not blocks:
        return []

    # Estimate dominant body font size
    sizes = [b["size"] for b in blocks]
    avg_size = sum(sizes) / len(sizes)
    heading_blocks = []

    for i, block in enumerate(blocks):
        if block["size"] >= avg_size * size_threshold:
            heading_blocks.append({
                "heading": block["text"],
                "page": block["page"],
                "index": i
            })

    return heading_blocks

def segment_under_headings(blocks, headings):
    segments = []
    for i, heading in enumerate(headings):
        start = heading["index"] + 1
        end = headings[i + 1]["index"] if i + 1 < len(headings) else len(blocks)
        content = " ".join([blocks[j]["text"] for j in range(start, end)])
        if content.strip():
            segments.append({
                "section_title": heading["heading"],
                "refined_text": content.strip(),
                "page_number": heading["page"]
            })
    return segments
