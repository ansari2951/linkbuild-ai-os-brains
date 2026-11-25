import json
import re
from pathlib import Path

from agents.publisher.research.researcher import run_research

ROOT = Path(__file__).resolve().parents[3]
SEED_FILE = ROOT / "knowledge" / "publisher" / "seed_urls.txt"
RESULTS_JSON = ROOT / "data" / "private" / "publisher_research" / "publisher_results.json"


def clean_command(command):
    return re.sub(r"^You\s*>\s*", "", (command or "").strip(), flags=re.I)


def research_publisher(command):
    command = clean_command(command)

    niche_match = re.search(
        r"\bfor\s+(.+?)(?:\s+in\s+|\s+market\s*$|$)",
        command,
        re.I
    )

    market_match = re.search(
        r"\bin\s+([A-Za-z ,]+)$",
        command,
        re.I
    )

    niche = niche_match.group(1).strip() if niche_match else "home improvement"
    if niche.lower() in ("publisher websites", "websites", ""):
        niche = "home improvement"
    market = market_match.group(1).strip() if market_match else "US"

    if not SEED_FILE.exists():
        return {
            "status": "needs_input",
            "message": "Publisher seed URL file is missing (knowledge/publisher/seed_urls.txt).",
            "niche": niche,
            "target_market": market,
        }

    # Execute live research against seed URLs when run directly or requested
    if "live" in command.lower() or not RESULTS_JSON.exists():
        run_research(niche)

    inspected_count = 0
    if RESULTS_JSON.exists():
        try:
            records = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
            inspected_count = len(records)
        except (OSError, json.JSONDecodeError):
            inspected_count = 0

    return {
        "status": "completed",
        "message": f"Publisher research ready for '{niche}' ({market}): {inspected_count} inspected publishers.",
        "niche": niche,
        "target_market": market,
        "publishers_inspected": inspected_count,
        "output_file": str(RESULTS_JSON),
    }
