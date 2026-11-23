
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Pipeline settings
PIPELINE_NAME = "LINKBUILD AI OS SEO Pipeline"

MAX_WEBSITES_PER_RUN = 10
CRAWLER_MAX_PAGES = 100
CRAWLER_MAX_DEPTH = 5
REQUEST_TIMEOUT = 20

# Safety settings
RESPECT_ROBOTS_TXT = True
ALLOW_EXTERNAL_CRAWLING = False
ALLOW_EMAIL_SENDING = False

# Input and output paths
INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "private"
    / "seo"
    / "pipeline"
    / "websites_input.csv"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "data"
    / "private"
    / "seo"
    / "pipeline"
)

STATUS_REPORT = REPORT_DIR / "seo_pipeline_status.csv"

# SEO modules
ENABLED_MODULES = {
    "crawler": True,
    "site_audit": True,
    "indexing": True,
    "schema": True,
    "redirects": True,
    "core_web_vitals": True,
    "images": True,
    "internal_links": True,
    "keyword_intelligence": True,
    "keyword_clustering": True,
    "content_gap": True,
    "competitor_intelligence": True,
}


def get_enabled_modules():
    return [
        name
        for name, enabled in ENABLED_MODULES.items()
        if enabled
    ]


def create_pipeline_directories():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    create_pipeline_directories()

    print(f"Pipeline: {PIPELINE_NAME}")
    print(f"Maximum websites: {MAX_WEBSITES_PER_RUN}")
    print(f"Crawler page limit: {CRAWLER_MAX_PAGES}")
    print(f"Enabled modules: {len(get_enabled_modules())}")
    print(f"Input file: {INPUT_FILE}")
    print("Configuration loaded successfully.")
