import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_VISION_MODEL = os.getenv("OPENROUTER_VISION_MODEL", "openai/gpt-4o-mini")

# When true, the pipeline skips the real OpenRouter vision call and uses a
# local color-heuristic mock instead. Useful for offline development/testing,
# or when the current network policy blocks outbound calls to openrouter.ai.
# The mock CANNOT identify plant species - it only estimates health from
# color statistics, purely to exercise the upload -> analyze -> display flow.
USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "false").lower() in {"1", "true", "yes"}

MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8 MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
