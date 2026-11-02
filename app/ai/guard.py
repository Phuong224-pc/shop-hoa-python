import time
import re
from typing import Dict, Tuple
from collections import deque
from config import Config

class RateLimiter:
    """
    In-memory sliding window rate limiter per client key (IP or user ID).
    """
    def __init__(self, max_requests: int = 20, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.history: Dict[str, deque] = {}

    def is_allowed(self, key: str) -> Tuple[bool, int]:
        """
        Returns (allowed, retry_after_seconds).
        """
        now = time.time()
        if key not in self.history:
            self.history[key] = deque()

        queue = self.history[key]
        # Evict timestamps older than the window
        while queue and (now - queue[0]) > self.window_seconds:
            queue.popleft()

        if len(queue) >= self.max_requests:
            oldest = queue[0]
            retry_after = max(1, int(self.window_seconds - (now - oldest)))
            return False, retry_after

        queue.append(now)
        return True, 0

# Common prompt injection patterns
INJECTION_PATTERNS = [
    r'ignore (all )?(previous|above) instructions',
    r'disregard (all )?(previous|above) instructions',
    r'bỏ qua (mọi )?(chỉ dẫn|hướng dẫn|lệnh) (trước|trên)',
    r'you are now in developer mode',
    r'dan mode',
    r'system prompt',
    r'reveal your secret',
    r'tiết lộ (prompt|hệ thống|mật khẩu|api key)',
    r'dump database',
    r'<script>',
    r'union select'
]

def check_prompt_injection(text: str) -> Tuple[bool, str]:
    """
    Check if the user input contains harmful instructions or prompt injection attempts.
    Returns (is_safe, warning_message).
    """
    if not text:
        return True, ""

    lower_text = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lower_text, re.IGNORECASE):
            return False, "Yêu cầu có dấu hiệu vi phạm nguyên tắc bảo mật thông tin."

    return True, ""

def sanitize_input(text: str, max_chars: int = 1500) -> str:
    """
    Sanitizes user query: limits length, normalizes whitespace.
    """
    if not text:
        return ""
    cleaned = text.replace('\x00', '').strip()
    return cleaned[:max_chars]

# Global instance
rate_limiter = RateLimiter(
    max_requests=getattr(Config, 'AI_RATE_LIMIT_PER_MINUTE', 20),
    window_seconds=60
)
