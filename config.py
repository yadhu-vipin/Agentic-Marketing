import os

# Redis and Celery Configurations
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Playwright Scraper Defaults
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
PAGE_TIMEOUT_MS = 30000

# Default Scoring Weights & Parameters (Total weight must equal 100)
DEFAULT_SCORING_WEIGHTS = {
    "has_phone": 20,
    "has_website": 15,
    "rating": 25,
    "menu_alignment": 25,
    "open_status": 15,
}

DEFAULT_MENU_ALIGNMENT_KEYWORDS = [
    "breakfast", "brunch", "sandwich", "toast",
    "artisan", "continental", "bakery", "cafe", "restaurant",
    "hotel", "bar", "pub", "sourdough", "food"
]

# Output paths
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
LEADS_OUTPUT_FILE = os.path.join(RESULTS_DIR, "leads_mode1.json")
CAMPAIGN_OUTPUT_FILE = os.path.join(RESULTS_DIR, "campaign_mode2.json")
CAMPAIGN_IMAGES_DIR = os.path.join(RESULTS_DIR, "campaign_images")

# Pollinations image generation (Mode 2)
POLLINATIONS_BASE_URL = os.getenv("POLLINATIONS_BASE_URL", "https://gen.pollinations.ai/image")
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")
POLLINATIONS_MODEL = os.getenv("POLLINATIONS_MODEL", "flux")
POLLINATIONS_WIDTH = int(os.getenv("POLLINATIONS_WIDTH", "1024"))
POLLINATIONS_HEIGHT = int(os.getenv("POLLINATIONS_HEIGHT", "1024"))
POLLINATIONS_TIMEOUT_SEC = int(os.getenv("POLLINATIONS_TIMEOUT_SEC", "120"))
POLLINATIONS_MAX_RETRIES = int(os.getenv("POLLINATIONS_MAX_RETRIES", "3"))
