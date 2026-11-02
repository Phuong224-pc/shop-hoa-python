import numpy as np
from typing import List, Dict, Any, Optional
from app.extensions import db
from app.models.ai import AiChunk
from app.ai.embeddings import default_embedder, Embedder
from app.ai.keywords import tokenize_vietnamese, calculate_bm25_score

class VectorStore:
    def __init__(self, embedder: Optional[Embedder] = None):
        self.embedder = embedder or default_embedder

    def save_chunk(self, source: str, ref_id: str, title: str, text: str,
                   chunk_index: int = 0, product_id: Optional[int] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   embedding: Optional[np.ndarray] = None) -> AiChunk:
        """
        Store a chunk and its embedding vector into SQLite ai_chunk table.
        """
        if embedding is None:
            embedding = self.embedder.embed_text(f"{title}\n{text}")

        chunk = AiChunk(
            source=source,
            ref_id=str(ref_id),
            product_id=product_id,
            chunk_index=chunk_index,
            title=title,
            text=text,
            model=self.embedder.model
        )
        chunk.set_embedding(embedding)
        chunk.set_metadata(metadata or {})

        db.session.add(chunk)
        return chunk

    def delete_by_source_and_ref(self, source: str, ref_id: str):
        """
        Delete chunks matching source and ref_id.
        """
        AiChunk.query.filter_by(source=source, ref_id=str(ref_id)).delete()
        db.session.commit()

    def hybrid_search(self, query: str,
                      source_filter: Optional[str] = None,
                      category_id: Optional[int] = None,
                      min_price: Optional[float] = None,
                      max_price: Optional[float] = None,
                      in_stock_only: bool = False,
                      alpha: float = 0.65,
                      top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Hybrid search combining semantic vector cosine similarity and keyword BM25.
        score = alpha * semantic_score + (1 - alpha) * keyword_score
        """
        query_vec = self.embedder.embed_text(query)
        query_tokens = tokenize_vietnamese(query)

        # 1. Database Pre-filtering
        q = AiChunk.query
        if source_filter:
            q = q.filter_by(source=source_filter)

        chunks: List[AiChunk] = q.all()
        if not chunks:
            return []

        scored_results = []
        for ch in chunks:
            meta = ch.get_metadata()

            # Pre-filter checks
            if category_id is not None and meta.get('category_id') != category_id:
                continue
            if min_price is not None and meta.get('price', 0) < min_price:
                continue
            if max_price is not None and meta.get('price', 0) > max_price:
                continue
            if in_stock_only and not meta.get('in_stock', True):
                continue

            # Semantic similarity
            ch_vec = ch.get_embedding()
            semantic_score = 0.0
            if ch_vec is not None and query_vec is not None and len(ch_vec) == len(query_vec):
                dot_prod = float(np.dot(query_vec, ch_vec))
                # Cosine is normalized since both are unit vectors
                semantic_score = max(0.0, min(1.0, (dot_prod + 1.0) / 2.0))

            # Keyword similarity
            doc_tokens = tokenize_vietnamese(f"{ch.title} {ch.text}")
            keyword_score = calculate_bm25_score(query_tokens, doc_tokens)
            # Normalize keyword score roughly to [0, 1]
            norm_kw_score = min(1.0, keyword_score / 5.0)

            final_score = (alpha * semantic_score) + ((1.0 - alpha) * norm_kw_score)

            scored_results.append({
                'chunk': ch,
                'score': round(final_score, 4),
                'semantic_score': round(semantic_score, 4),
                'keyword_score': round(norm_kw_score, 4),
                'title': ch.title,
                'text': ch.text,
                'source': ch.source,
                'ref_id': ch.ref_id,
                'product_id': ch.product_id,
                'metadata': meta
            })

        scored_results.sort(key=lambda x: x['score'], reverse=True)
        return scored_results[:top_k]

# Global instance
default_vector_store = VectorStore()

