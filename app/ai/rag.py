import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
from app.extensions import db
from app.models.ai import AiChunk
from app.models.catalog import Product, Category, Occasion
from app.ai.chunking import split_markdown_by_headers
from app.ai.vectorstore import default_vector_store
from app.ai.prompts import SYSTEM_FLOWER_RAG
from app.ai.llm import default_llm
from config import BASE_DIR

DOCS_DIR = Path(__file__).resolve().parent / 'docs'

def extract_budget_from_query(query: str) -> Optional[float]:
    """
    Extract budget limit like 'dưới 500k', 'dưới 500 nghìn', 'dưới 1 triệu'.
    """
    q = query.lower()
    # Match patterns like 'dưới 500k', 'dưới 500.000', '< 500k'
    m_k = re.search(r'(?:dưới|<|khoảng|tầm)\s*(\d+)\s*(?:k|nghìn|ngàn)', q)
    if m_k:
        try:
            return float(m_k.group(1)) * 1000.0
        except Exception:
            pass

    m_trieu = re.search(r'(?:dưới|<|khoảng|tầm)\s*(\d+(?:\.\d+)?)\s*(?:tr|triệu)', q)
    if m_trieu:
        try:
            return float(m_trieu.group(1)) * 1000000.0
        except Exception:
            pass

    m_vnd = re.search(r'(?:dưới|<)\s*(\d{2,3}(?:\.\d{3})+)', q)
    if m_vnd:
        try:
            clean_num = m_vnd.group(1).replace('.', '')
            return float(clean_num)
        except Exception:
            pass

    return None

def index_all_docs() -> int:
    """
    Index all markdown policy files from app/ai/docs/.
    """
    if not DOCS_DIR.exists():
        return 0

    count = 0
    # Remove existing doc chunks
    AiChunk.query.filter_by(source='doc').delete()

    for md_file in DOCS_DIR.glob('*.md'):
        filename = md_file.name
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        sections = split_markdown_by_headers(content)
        for idx, sec in enumerate(sections):
            default_vector_store.save_chunk(
                source='doc',
                ref_id=filename,
                title=f"{sec['title']} ({filename})",
                text=sec['text'],
                chunk_index=idx,
                metadata={'filename': filename, 'doc_title': sec['title']}
            )
            count += 1

    db.session.commit()
    return count

def index_all_products(rebuild: bool = False) -> int:
    """
    Index all active published products into AiChunk table.
    """
    if rebuild:
        AiChunk.query.filter_by(source='product').delete()

    products = Product.query.filter_by(status='PUBLISHED').all()
    count = 0
    for prod in products:
        index_single_product(prod.id, commit=False)
        count += 1

    db.session.commit()
    return count

def index_single_product(product_id: int, commit: bool = True):
    """
    Index or re-index a single product by ID.
    """
    prod = Product.query.get(product_id)
    if not prod:
        return

    # Delete old chunks for this product
    AiChunk.query.filter_by(source='product', ref_id=str(product_id)).delete()

    if prod.status != 'PUBLISHED':
        if commit:
            db.session.commit()
        return

    var = prod.default_variant
    price = float(var.effective_price) if var else 0.0
    stock = var.stock if var else 0
    in_stock = stock > 0

    cat_name = prod.primary_category.name if prod.primary_category else "Hoa nghệ thuật"
    occasions = ", ".join([o.name for o in prod.occasions]) if hasattr(prod, 'occasions') else ""
    flower_types = ", ".join([f.name for f in prod.flower_types]) if hasattr(prod, 'flower_types') else ""

    text = (
        f"Mẫu hoa: {prod.name}\n"
        f"Mã SKU: {prod.sku}\n"
        f"Danh mục kiểu dáng: {cat_name}\n"
        f"Dịp tặng phù hợp: {occasions}\n"
        f"Loại hoa thành phần: {flower_types}\n"
        f"Đơn giá niêm yết: {price:,.0f} đ\n"
        f"Trạng thái tồn kho: {'Còn hàng' if in_stock else 'Hết hàng'} (Số lượng: {stock})\n"
        f"Mô tả sản phẩm: {prod.short_description}\n"
        f"Chi tiết và cảm xúc: {prod.description}\n"
        f"Thành phần hoa phối: {prod.flower_composition}\n"
        f"Ý nghĩa và hướng dẫn: {prod.care_instructions}"
    )

    metadata = {
        'product_id': prod.id,
        'sku': prod.sku,
        'name': prod.name,
        'slug': prod.slug,
        'price': price,
        'in_stock': in_stock,
        'stock': stock,
        'category_id': prod.primary_category_id,
        'category_name': cat_name,
        'image': prod.main_image_url or '/static/images/placeholder.jpg'
    }

    default_vector_store.save_chunk(
        source='product',
        ref_id=str(prod.id),
        title=f"Mẫu hoa: {prod.name} ({price:,.0f} đ)",
        text=text,
        chunk_index=0,
        product_id=prod.id,
        metadata=metadata
    )

    if commit:
        db.session.commit()

def delete_product_index(product_id: int):
    """
    Remove product chunks from vectorstore.
    """
    AiChunk.query.filter_by(source='product', ref_id=str(product_id)).delete()
    db.session.commit()

def build_rag_context(query: str, top_k: int = 5) -> Tuple_RAG:
    """
    Retrieves matching chunks and builds numbered context string with citations.
    """
    budget_limit = extract_budget_from_query(query)
    results = default_vector_store.hybrid_search(
        query=query,
        max_price=budget_limit,
        top_k=top_k
    )

    context_lines = []
    citations = []
    product_cards = []
    seen_products = set()

    for idx, item in enumerate(results, start=1):
        ch = item['chunk']
        context_lines.append(f"[{idx}] {ch.title}\n{ch.text}\n")
        citations.append({
            'index': idx,
            'title': ch.title,
            'source': ch.source,
            'ref_id': ch.ref_id,
            'product_id': ch.product_id
        })

        if ch.source == 'product' and ch.product_id and ch.product_id not in seen_products:
            seen_products.add(ch.product_id)
            meta = ch.get_metadata()
            product_cards.append({
                'id': ch.product_id,
                'name': meta.get('name', ch.title),
                'slug': meta.get('slug', ''),
                'price': meta.get('price', 0),
                'in_stock': meta.get('in_stock', True),
                'image': meta.get('image', '/static/images/placeholder.jpg')
            })

    context_str = "\n".join(context_lines) if context_lines else "Hiện chưa có tài liệu cụ thể phù hợp với yêu cầu này."
    return context_str, citations, product_cards

class Tuple_RAG:
    # Helper type
    pass

def ask_flower_assistant(query: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """
    Generate an grounded response with citations and product cards.
    """
    context_str, citations, product_cards = build_rag_context(query)

    # Build prompt with optional short history
    prompt_parts = []
    prompt_parts.append(f"[NGỮ CẢNH CỬA HÀNG ĐÃ XÁC NHẬN]:\n{context_str}\n")

    if history:
        # Keep max 3 recent turns
        prompt_parts.append("[LỊCH SỬ HỘI THOẠI GẦN ĐÂY]:")
        for turn in history[-3:]:
            role = "Khách hàng" if turn.get('role') == 'user' else "Trợ lý Flora"
            prompt_parts.append(f"{role}: {turn.get('content', '')}")
        prompt_parts.append("")

    prompt_parts.append(f"Câu hỏi của Khách hàng: {query}")
    full_prompt = "\n".join(prompt_parts)

    answer = default_llm.generate(
        prompt=full_prompt,
        system_instruction=SYSTEM_FLOWER_RAG
    )

    return {
        'answer': answer,
        'citations': citations,
        'products': product_cards
    }

def stream_flower_assistant(query: str, history: Optional[List[Dict[str, str]]] = None) -> Generator[Dict[str, Any], None, None]:
    """
    Stream answer chunks followed by metadata (citations & product cards).
    """
    context_str, citations, product_cards = build_rag_context(query)

    prompt_parts = []
    prompt_parts.append(f"[NGỮ CẢNH CỬA HÀNG ĐÃ XÁC NHẬN]:\n{context_str}\n")

    if history:
        prompt_parts.append("[LỊCH SỬ HỘI THOẠI GẦN ĐÂY]:")
        for turn in history[-3:]:
            role = "Khách hàng" if turn.get('role') == 'user' else "Trợ lý Flora"
            prompt_parts.append(f"{role}: {turn.get('content', '')}")
        prompt_parts.append("")

    prompt_parts.append(f"Câu hỏi của Khách hàng: {query}")
    full_prompt = "\n".join(prompt_parts)

    for chunk in default_llm.stream_generate(prompt=full_prompt, system_instruction=SYSTEM_FLOWER_RAG):
        yield {'type': 'text', 'content': chunk}

    # Final metadata event
    yield {
        'type': 'meta',
        'citations': citations,
        'products': product_cards
    }
