import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reviews.db")
NEGATIVE_ALERT_THRESHOLD = int(os.getenv("NEGATIVE_ALERT_THRESHOLD", "2"))

# When true, the pipeline skips the real OpenRouter call and uses a local
# heuristic instead. Useful for offline development/testing, or when the
# current network policy blocks outbound calls to openrouter.ai.
USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "false").lower() in {"1", "true", "yes"}
