import hashlib
import numpy as np
from typing import List, Optional
from flask import current_app
from config import Config

class Embedder:
    def __init__(self, mode: Optional[str] = None, model: Optional[str] = None):
        self.mode = (mode or getattr(Config, 'AI_MODE', 'gemini')).lower()
        self.model = model or getattr(Config, 'GEMINI_EMBED_MODEL', 'gemini-embedding-001')
        self._client = None

    def _get_genai_client(self):
        if self._client is None:
            from google import genai
            api_key = getattr(Config, 'GEMINI_API_KEY', '')
            if not api_key:
                raise ValueError("Chưa cấu hình GEMINI_API_KEY trong file .env")
            self._client = genai.Client(api_key=api_key)
        return self._client

    @property
    def active_mode(self):
        try:
            from flask import current_app
            if current_app:
                return current_app.config.get('AI_MODE', self.mode).lower()
        except Exception:
            pass
        return self.mode

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embed a single text string into a normalized numpy vector (L2 norm = 1.0).
        """
        if not text or not text.strip():
            return np.zeros(64, dtype=np.float32)

        if self.active_mode == 'gemini':
            try:
                client = self._get_genai_client()
                response = client.models.embed_content(
                    model=self.model,
                    contents=text
                )
                if hasattr(response, 'embeddings') and response.embeddings:
                    vec = np.array(response.embeddings[0].values, dtype=np.float32)
                elif hasattr(response, 'embedding') and response.embedding:
                    vec = np.array(response.embedding.values, dtype=np.float32)
                else:
                    raise ValueError("Không nhận được vector embedding từ Gemini API")

                norm = np.linalg.norm(vec)
                return vec / norm if norm > 0 else vec
            except Exception as e:
                # If Gemini API fails, raise error so user knows instead of silently generating fake vectors
                raise RuntimeError(f"Lỗi khi gọi Gemini Embedding API ({self.model}): {e}") from e

        # Fallback local / mock deterministic embedding (for CI/CD and testing)
        return self._deterministic_hash_vector(text, dim=64)

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Embed a list of text strings.
        """
        return [self.embed_text(t) for t in texts]

    def _deterministic_hash_vector(self, text: str, dim: int = 64) -> np.ndarray:
        """
        Generates a deterministic normalized pseudo-vector based on word hashing.
        Useful for offline testing and reproducible tests.
        """
        vec = np.zeros(dim, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec

        for word in words:
            h = int(hashlib.sha256(word.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            val = ((h >> 8) % 1000) / 1000.0 - 0.5
            vec[idx] += val

        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

# Global singleton embedder
default_embedder = Embedder()
