from pathlib import Path
import os
from dotenv import load_dotenv

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Main directories
DATA_DIR = PROJECT_ROOT / "data"
PRIVATE_DATA_DIR = DATA_DIR / "private"
PUBLIC_DATA_DIR = DATA_DIR / "public"

LOGS_DIR = PRIVATE_DATA_DIR / "system"
EXPORTS_DIR = DATA_DIR / "exports"

# Project settings
APP_NAME = "LINKBUILD AI OS"
APP_VERSION = "1.0.0"
APP_ENV = os.getenv("APP_ENV", "local")

# Safety settings
SEND_EMAILS = os.getenv("SEND_EMAILS", "false").lower() == "true"
REQUIRE_EMAIL_APPROVAL = True

# AI settings
AI_PROVIDER = os.getenv("AI_PROVIDER", "auto").lower()

# Legacy compatibility
AI_API_KEY = os.getenv("AI_API_KEY", "")

# AI API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# AI model settings
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Email settings
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Create required directories
for directory in [
    PRIVATE_DATA_DIR,
    PUBLIC_DATA_DIR,
    LOGS_DIR,
    EXPORTS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)