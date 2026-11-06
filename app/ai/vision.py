import re
from typing import Dict, Any, List, Optional
from app.extensions import db
from app.models.catalog import Product
from app.ai.llm import default_llm
from app.ai.vectorstore import default_vector_store

SYSTEM_FLOWER_VISION = """Bạn là Chuyên gia Thực vật học và Nghệ nhân cắm hoa cao cấp (Florist Master) tại Flora Flower Boutique.
Nhiệm vụ của bạn là quan sát và phân tích bức ảnh hoa tươi mà khách hàng cung cấp.
Hãy trả lời với văn phong thanh lịch, ấm áp, tinh tế của thương hiệu Flora Flower Boutique.

Cấu trúc câu trả lời:
1. 🌸 **Loài hoa được nhận diện:** Nêu tên tiếng Việt chính xác, tên tiếng Anh hoặc tên khoa học nếu có.
2. 🎨 **Màu sắc & Đặc điểm:** Mô tả tông màu, dáng cánh, nét độc đáo của mẫu hoa trong ảnh.
3. ✨ **Ý nghĩa & Dịp tặng phù hợp:** Giải thích ý nghĩa biểu tượng (sinh nhật, tình yêu, khai trương, tốt nghiệp, tỏ tình, cảm ơn...) và đối tượng người nhận phù hợp.
4. 💧 **Mẹo giữ hoa tươi lâu:** 2-3 gạch đầu dòng hướng dẫn chăm sóc cơ bản.

Cuối cùng, PHẢI THÊM chính xác 2 dòng sau vào cuối phản hồi để hệ thống tự động đối soát sản phẩm:
[FLOWER_NAME: <tên loài hoa chính, ví dụ: hoa hồng, hoa hướng dương, hoa cẩm tú cầu, hoa tulip, hoa lan hồ điệp, hoa cẩm chướng...>]
[KEYWORDS: <3-5 từ khóa tiếng Việt không dấu hoặc có dấu cách nhau bằng dấu phẩy, ví dụ: hồng, juliet, cam, bó hoa>]
"""

def analyze_flower_image_and_recommend(image_bytes: bytes, mime_type: str = 'image/jpeg', user_prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    1. Sends image to Gemini Vision to identify flower species, meaning and characteristics.
    2. Searches store database & vectorstore for matching products.
    3. Returns analysis text and recommended product cards.
    """
    prompt = user_prompt.strip() if user_prompt and user_prompt.strip() else "Hãy nhận diện bức ảnh hoa này là hoa gì, ý nghĩa và gợi ý dịp tặng phù hợp."

    analysis_raw = default_llm.generate_with_image(
        prompt=prompt,
        image_bytes=image_bytes,
        mime_type=mime_type,
        system_instruction=SYSTEM_FLOWER_VISION
    )

    # Extract flower name and keywords from tags
    flower_name = ""
    keywords: List[str] = []

    fn_match = re.search(r'\[FLOWER_NAME:\s*([^\]]+)\]', analysis_raw, re.IGNORECASE)
    if fn_match:
        flower_name = fn_match.group(1).strip()

    kw_match = re.search(r'\[KEYWORDS:\s*([^\]]+)\]', analysis_raw, re.IGNORECASE)
    if kw_match:
        raw_kws = kw_match.group(1).split(',')
        keywords = [k.strip() for k in raw_kws if k.strip()]

    # Clean display text (remove the system tags)
    clean_answer = re.sub(r'\[FLOWER_NAME:[^\]]+\]', '', analysis_raw)
    clean_answer = re.sub(r'\[KEYWORDS:[^\]]+\]', '', clean_answer).strip()

    # If flower_name is still empty, try extracting common flowers from clean_answer
    common_flowers = ['hồng', 'hướng dương', 'cẩm tú cầu', 'baby', 'tulip', 'lan hồ điệp', 'cúc', 'sen', 'cát tường', 'đồng tiền', 'mẫu đơn']
    if not flower_name:
        for f in common_flowers:
            if f in clean_answer.lower():
                flower_name = f"Hoa {f}"
                keywords.append(f)
                break

    # Search for matching products in our database
    recommended_products = search_matching_products(flower_name, keywords)

    return {
        'success': True,
        'answer': clean_answer,
        'flower_name': flower_name or 'Hoa tươi nghệ thuật',
        'keywords': keywords,
        'products': recommended_products
    }

def search_matching_products(flower_name: str, keywords: List[str], limit: int = 4) -> List[Dict[str, Any]]:
    """
    Find relevant products in Flora Flower catalog by name, composition, description or vector similarity.
    """
    found_products = []
    seen_ids = set()

    search_terms = []
    if flower_name:
        clean_fn = re.sub(r'^(hoa|bó hoa|giỏ hoa)\s+', '', flower_name, flags=re.IGNORECASE).strip()
        search_terms.append(clean_fn)
        for w in clean_fn.split():
            if len(w) > 2 and w.lower() not in ['hoa', 'tươi', 'loài']:
                search_terms.append(w)

    for kw in keywords:
        if kw and kw not in search_terms:
            search_terms.append(kw)

    # 1. Database query on Product
    base_query = Product.query.filter_by(status='PUBLISHED')

    for term in search_terms:
        if len(found_products) >= limit:
            break
        matched = base_query.filter(
            (Product.name.ilike(f"%{term}%")) |
            (Product.flower_composition.ilike(f"%{term}%")) |
            (Product.description.ilike(f"%{term}%"))
        ).all()

        for p in matched:
            if p.id not in seen_ids:
                seen_ids.add(p.id)
                found_products.append(p)
                if len(found_products) >= limit:
                    break

    # 2. Hybrid vector search if we need more products
    if len(found_products) < limit and search_terms:
        try:
            v_results = default_vector_store.hybrid_search(
                query=" ".join(search_terms[:3]),
                top_k=limit
            )
            for item in v_results:
                ch = item['chunk']
                if ch.source == 'product' and ch.product_id and ch.product_id not in seen_ids:
                    p = Product.query.get(ch.product_id)
                    if p and p.status == 'PUBLISHED':
                        seen_ids.add(p.id)
                        found_products.append(p)
                        if len(found_products) >= limit:
                            break
        except Exception:
            pass

    # 3. Fallback: If still no matches (rare flower not in stock), recommend bestselling products
    if not found_products:
        fallbacks = Product.query.filter_by(status='PUBLISHED').order_by(Product.is_featured.desc(), Product.created_at.desc()).limit(limit).all()
        for p in fallbacks:
            if p.id not in seen_ids:
                seen_ids.add(p.id)
                found_products.append(p)

    # Format products for JSON frontend
    cards = []
    for p in found_products[:limit]:
        def_v = p.default_variant
        price = int(p.min_price) if p.min_price else (int(def_v.effective_price) if def_v else 0)
        img_url = p.main_image.url if p.main_image else '/static/images/placeholder.jpg'

        cards.append({
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'sku': p.sku,
            'price': price,
            'in_stock': p.is_active,
            'image': img_url,
            'url': f"/products/{p.slug}"
        })

    return cards

