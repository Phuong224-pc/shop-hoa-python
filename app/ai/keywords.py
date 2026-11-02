import re
import math
from typing import List, Dict, Set

# Common Vietnamese stopwords in e-commerce
VIETNAMESE_STOPWORDS: Set[str] = {
    'và', 'của', 'là', 'có', 'cho', 'với', 'trong', 'được', 'các', 'những',
    'để', 'khi', 'về', 'này', 'đó', 'từ', 'theo', 'ra', 'vào', 'ở', 'tại',
    'thì', 'sẽ', 'đã', 'đang', 'rất', 'nhiều', 'hơn', 'một', 'hai', 'ba',
    'bằng', 'như', 'nhưng', 'bởi', 'vì', 'do', 'đến', 'lại', 'nên', 'cũng',
    'làm', 'hay', 'hoặc', 'nếu', 'thế', 'thì', 'gì', 'sao', 'nào', 'ai', 'ngày'
}

def tokenize_vietnamese(text: str) -> List[str]:
    """
    Cleans text and extracts unigrams and bigrams.
    """
    if not text:
        return []
    # Lowercase and replace non-alphanumeric (keeping Vietnamese accents)
    clean_text = re.sub(r'[^\w\s]', ' ', text.lower(), flags=re.UNICODE)
    raw_tokens = clean_text.split()
    tokens = [t for t in raw_tokens if len(t) > 1 and t not in VIETNAMESE_STOPWORDS]

    # Add meaningful consecutive bigrams
    bigrams = []
    for i in range(len(raw_tokens) - 1):
        w1, w2 = raw_tokens[i], raw_tokens[i+1]
        if w1 not in VIETNAMESE_STOPWORDS and w2 not in VIETNAMESE_STOPWORDS:
            bigrams.append(f"{w1}_{w2}")

    return tokens + bigrams

def calculate_bm25_score(query_tokens: List[str], doc_tokens: List[str], avg_doc_len: float = 100.0, k1: float = 1.5, b: float = 0.75) -> float:
    """
    Calculate BM25 relevance score between query tokens and document tokens.
    """
    if not query_tokens or not doc_tokens:
        return 0.0

    doc_len = len(doc_tokens)
    doc_freqs: Dict[str, int] = {}
    for t in doc_tokens:
        doc_freqs[t] = doc_freqs.get(t, 0) + 1

    score = 0.0
    for q in query_tokens:
        if q in doc_freqs:
            tf = doc_freqs[q]
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_len / (avg_doc_len or 1.0)))
            score += (numerator / denominator)

    return float(score)
