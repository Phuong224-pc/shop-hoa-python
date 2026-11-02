import re
from typing import List, Dict, Any

def split_markdown_by_headers(markdown_text: str, max_chunk_chars: int = 1200) -> List[Dict[str, Any]]:
    """
    Split a Markdown document by # and ## headers.
    If a section is too long, falls back to sliding window.
    """
    lines = markdown_text.splitlines()
    sections: List[Dict[str, Any]] = []
    current_title = "Giới thiệu chung"
    current_lines: List[str] = []

    for line in lines:
        header_match = re.match(r'^(#{1,3})\s+(.+)$', line.strip())
        if header_match:
            if current_lines:
                text_content = "\n".join(current_lines).strip()
                if text_content:
                    sections.append({
                        'title': current_title,
                        'text': text_content
                    })
                current_lines = []
            current_title = header_match.group(2).strip()
        else:
            current_lines.append(line)

    if current_lines:
        text_content = "\n".join(current_lines).strip()
        if text_content:
            sections.append({
                'title': current_title,
                'text': text_content
            })

    chunks: List[Dict[str, Any]] = []
    for s in sections:
        if len(s['text']) <= max_chunk_chars:
            chunks.append(s)
        else:
            sub_chunks = sliding_window_chunk(s['text'], chunk_size=800, overlap=150)
            for idx, sc in enumerate(sub_chunks):
                chunks.append({
                    'title': f"{s['title']} (Phần {idx + 1})",
                    'text': sc
                })

    return chunks


def sliding_window_chunk(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """
    Splits arbitrary text into overlapping chunks by word boundaries.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    total_words = len(words)
    words_per_chunk = max(30, chunk_size // 6)
    overlap_words = max(10, overlap // 6)

    while start < total_words:
        end = min(start + words_per_chunk, total_words)
        chunk_text = " ".join(words[start:end]).strip()
        if chunk_text:
            chunks.append(chunk_text)
        if end >= total_words:
            break
        start += (words_per_chunk - overlap_words)

    return chunks

