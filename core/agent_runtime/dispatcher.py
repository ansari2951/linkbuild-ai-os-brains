
import csv
from pathlib import Path
from core.master_brain.registry import get_agent
from agents.publisher.research.brain import research_publisher
import agents.email.extractor.outreach_generator as outreach_gen
import agents.email.negotiation.negotiation as neg_engine
import agents.clients.prospecting.client_prospecting as client_engine
import agents.email.extractor.intelligence as email_intel

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def handle_publisher_outreach(command):
    try:
        outreach_gen.main()
        draft_file = PROJECT_ROOT / "data" / "private" / "email_extraction" / "outreach_drafts.csv"
        count = 0
        if draft_file.exists():
            with open(draft_file, "r", encoding="utf-8-sig") as f:
                count = sum(1 for _ in csv.DictReader(f))
        return {
            "status": "completed",
            "message": f"Generated {count} personalized publisher outreach drafts.",
            "output_file": str(draft_file),
            "drafts_count": count
        }
    except Exception as error:
        return {"status": "failed", "message": f"Outreach generation failed: {error}"}


def handle_publisher_deals(command):
    try:
        neg_engine.main()
        res_file = PROJECT_ROOT / "data" / "private" / "email_extraction" / "negotiation_results.csv"
        count = 0
        if res_file.exists():
            with open(res_file, "r", encoding="utf-8-sig") as f:
                count = sum(1 for _ in csv.DictReader(f))
        return {
            "status": "completed",
            "message": f"Processed {count} publisher price negotiations and draft counter-offers.",
            "output_file": str(res_file),
            "negotiations_count": count
        }
    except Exception as error:
        return {"status": "failed", "message": f"Deal negotiation analysis failed: {error}"}


def handle_client_research(command):
    try:
        client_engine.main()
        out_file = PROJECT_ROOT / "data" / "private" / "client_prospecting" / "client_prospects.csv"
        count = 0
        if out_file.exists():
            with open(out_file, "r", encoding="utf-8-sig") as f:
                count = sum(1 for _ in csv.DictReader(f))
        return {
            "status": "completed",
            "message": f"Discovered and scored {count} high-priority client link building prospects.",
            "output_file": str(out_file),
            "prospects_count": count
        }
    except Exception as error:
        return {"status": "failed", "message": f"Client prospecting failed: {error}"}


def handle_client_outreach(command):
    try:
        in_file = PROJECT_ROOT / "data" / "private" / "client_prospecting" / "client_prospects.csv"
        out_file = PROJECT_ROOT / "data" / "private" / "client_prospecting" / "client_outreach_pitches.csv"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        
        pitches = []
        if in_file.exists():
            with open(in_file, "r", encoding="utf-8-sig") as f:
                for row in csv.DictReader(f):
                    company = row.get("company_name", "Team")
                    email = row.get("email", "")
                    services = row.get("services", "SEO")
                    pitches.append({
                        "company_name": company,
                        "email": email,
                        "subject": f"Authority Link Building & Guest Post Growth for {company}",
                        "proposal": f"Hi {company} team,\n\nI noticed your focus on {services}. We have secured placements on top publications that can boost your organic authority. Would you like a custom link profile audit?\n\nBest regards,\nLINKBUILD AI OS Team",
                        "status": "DRAFT_READY"
                    })

        if pitches:
            with open(out_file, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(pitches[0].keys()))
                writer.writeheader()
                writer.writerows(pitches)

        return {
            "status": "completed",
            "message": f"Drafted {len(pitches)} client acquisition outreach proposals.",
            "output_file": str(out_file),
            "pitches_count": len(pitches)
        }
    except Exception as error:
        return {"status": "failed", "message": f"Client outreach failed: {error}"}


def handle_email_intelligence(command):
    try:
        email_intel.main()
        intel_file = PROJECT_ROOT / "data" / "private" / "email_extraction" / "contact_intelligence.csv"
        count = 0
        if intel_file.exists():
            with open(intel_file, "r", encoding="utf-8-sig") as f:
                count = sum(1 for _ in csv.DictReader(f))
        return {
            "status": "completed",
            "message": f"Analyzed {count} contact email records with MX resolution and role classification.",
            "output_file": str(intel_file),
            "contacts_analyzed": count
        }
    except Exception as error:
        return {"status": "failed", "message": f"Email intelligence failed: {error}"}


AGENT_HANDLERS = {
    "publisher_research": research_publisher,
    "publisher_outreach": handle_publisher_outreach,
    "publisher_deals": handle_publisher_deals,
    "client_research": handle_client_research,
    "client_outreach": handle_client_outreach,
    "email_intelligence": handle_email_intelligence,
}


def execute_agent(agent_id, command):
    agent = get_agent(agent_id)

    if agent is None:
        return {
            "status": "failed",
            "message": f"Unknown agent: {agent_id}"
        }

    handler = AGENT_HANDLERS.get(agent_id)

    if handler is None:
        return {
            "status": "needs_input",
            "message": (
                f"{agent['name']} is registered, "
                "but its execution handler is not connected yet."
            )
        }

    try:
        result = handler(command)

        if isinstance(result, dict):
            return result

        return {
            "status": "needs_input",
            "message": "Agent returned an unsupported result format."
        }

    except Exception as error:
        return {
            "status": "failed",
            "message": str(error)
        }
