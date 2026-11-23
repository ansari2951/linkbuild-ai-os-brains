import re


def clean_command(command):
    return re.sub(r"^You\s*>\s*", "", command.strip(), flags=re.I)


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

    niche = niche_match.group(1).strip() if niche_match else None
    market = market_match.group(1).strip() if market_match else None

    if not niche or niche.lower() in ("publisher websites", "websites"):
        return {
            "status": "needs_input",
            "message": "Publisher research needs a specific niche.",
            "required_information": [
                "Target niche",
                "Target country",
                "Preferred website type"
            ]
        }

    if not market:
        return {
            "status": "needs_input",
            "message": "Please specify the target country.",
            "niche": niche,
            "required_information": ["Target country"]
        }

    return {
        "status": "ready_for_research",
        "message": "Research requirements successfully collected.",
        "niche": niche,
        "target_market": market,
        "research_mode": "planning_only"
    }
