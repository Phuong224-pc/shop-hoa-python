import time
from typing import Generator, Optional, List, Dict
from config import Config

class GeminiLLM:
    def __init__(self, mode: Optional[str] = None, model: Optional[str] = None, api_key: Optional[str] = None):
        self.mode = (mode or getattr(Config, 'AI_MODE', 'gemini')).lower()
        self.model = model or getattr(Config, 'GEMINI_MODEL', 'gemini-3.5-flash-lite')
        self.api_key = api_key or getattr(Config, 'GEMINI_API_KEY', '')
        self._client = None

    def _get_client(self):
        if self._client is None:
            if not self.api_key:
                raise ValueError("Chưa thiết lập GEMINI_API_KEY trong file .env. Vui lòng cấu hình khóa để sử dụng AI thật.")
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
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

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Generate text completion from Gemini.
        """
        if self.active_mode in ['mock', 'demo']:
            return self._mock_response(prompt)

        client = self._get_client()
        try:
            config_params = {}
            if system_instruction:
                config_params['system_instruction'] = system_instruction

            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config_params if config_params else None
            )
            return response.text or ""
        except Exception as e:
            # Fallback model attempt if primary is busy or unavailable
            if "503" in str(e) or "404" in str(e):
                fallback_models = ['gemini-3.5-flash', 'gemini-3.8-flash', 'gemini-flash-latest']
                for fb_model in fallback_models:
                    if fb_model != self.model:
                        try:
                            response = client.models.generate_content(
                                model=fb_model,
                                contents=prompt,
                                config=config_params if config_params else None
                            )
                            return response.text or ""
                        except Exception:
                            continue
            raise RuntimeError(f"Lỗi kết nối Gemini API ({self.model}): {e}") from e

    def stream_generate(self, prompt: str, system_instruction: Optional[str] = None) -> Generator[str, None, None]:
        """
        Stream text chunks from Gemini.
        """
        if self.mode == 'mock' or self.mode == 'demo':
            simulated = self._mock_response(prompt)
            words = simulated.split()
            for w in words:
                yield w + " "
                time.sleep(0.02)
            return

        client = self._get_client()
        try:
            config_params = {}
            if system_instruction:
                config_params['system_instruction'] = system_instruction

            response_stream = client.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=config_params if config_params else None
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            raise RuntimeError(f"Lỗi streaming từ Gemini API: {e}") from e

    def _mock_response(self, prompt: str) -> str:
        """
        Coherent offline mock response for unit tests.
        """
        if "tóm tắt" in prompt.lower() or "summarize" in prompt.lower():
            return "Bó hoa tươi nghệ thuật phối màu trang nhã, mang phong cách sang trọng và cảm xúc ấm áp cho người nhận."
        if "hashtag" in prompt.lower():
            return "#FloraFlower #HoaSinhNhat #HoaTuoiSaiGon #FloristArt #BoutiqueFlower"
        if "dịch" in prompt.lower() or "translate" in prompt.lower():
            return "An exquisite fresh flower arrangement featuring premium roses with delicate pastel tones."
        return "Chào bạn! Tôi là trợ lý ảo Flora Flower. Tôi có thể giúp bạn chọn hoa theo dịp, ngân sách hoặc giải đáp chính sách giao hàng và bảo hành."

# Global LLM instance
default_llm = GeminiLLM()
