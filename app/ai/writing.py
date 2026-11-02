from typing import List
from app.ai.llm import default_llm
from app.ai.prompts import (
    PROMPT_SUMMARIZE, PROMPT_HASHTAGS,
    PROMPT_REWRITE, PROMPT_TRANSLATE
)

def summarize_description(text: str) -> str:
    """
    Summarize product description into 2-3 sentences.
    """
    if not text or not text.strip():
        return ""
    prompt = PROMPT_SUMMARIZE.format(text=text.strip())
    return default_llm.generate(prompt)

def suggest_hashtags(text: str, product_name: str = "") -> List[str]:
    """
    Suggest hashtags for social media / SEO.
    """
    prompt = PROMPT_HASHTAGS.format(name=product_name or "Mẫu hoa tươi", text=text or "")
    resp = default_llm.generate(prompt)
    # Parse tokens starting with #
    tags = [w.strip() for w in resp.split() if w.startswith('#')]
    if not tags:
        # Fallback split
        tags = [f"#{w.strip()}" for w in resp.replace(',', ' ').split() if w.strip()]
    return tags[:10]

def rewrite_boutique_style(text: str, style: str = "lãng mạn, thơ mộng") -> str:
    """
    Rewrite description into boutique florist tone.
    """
    if not text or not text.strip():
        return ""
    prompt = PROMPT_REWRITE.format(style=style, text=text.strip())
    return default_llm.generate(prompt)

def translate_description(text: str, target_lang: str = "tiếng Anh") -> str:
    """
    Translate description to target language (English/Vietnamese).
    """
    if not text or not text.strip():
        return ""
    prompt = PROMPT_TRANSLATE.format(target_lang=target_lang, text=text.strip())
    return default_llm.generate(prompt)

