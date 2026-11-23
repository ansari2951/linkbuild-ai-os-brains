
import importlib.util
import json
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = BASE_DIR / "data" / "private" / "system"
LOG_FILE = LOG_DIR / "brain_logs.jsonl"

AGENTS = {
    "email_extractor": "agents/email/extractor/engine.py",
    "email_validator": "agents/email/extractor/validator.py",
    "email_classifier": "agents/email/extractor/classifier.py",
    "contact_intelligence": "agents/email/extractor/intelligence.py",
    "outreach_generator": "agents/email/extractor/outreach_generator.py",
    "approval_manager": "agents/email/extractor/approval_manager.py",
    "email_sender": "agents/email/extractor/sender.py",
    "outreach_personalizer": "agents/email/personalizer/personalizer.py",
    "reply_detector": "agents/email/reply_detector/reply_detector.py",
    "negotiation": "agents/email/negotiation/negotiation.py",
    "publisher_crm": "agents/publisher/crm/publisher_crm.py",
    "website_discovery": "agents/publisher/discovery/website_discovery.py",
    "client_prospecting": "agents/clients/prospecting/client_prospecting.py",
}


class CentralBrain:

    def __init__(self):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.agents = AGENTS.copy()

    def log_event(self, event, details=None):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "details": details or {}
        }

        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write(json.dumps(record) + "\n")

    def get_agent_status(self):
        results = {}

        for name, relative_path in self.agents.items():
            file_path = BASE_DIR / relative_path

            results[name] = {
                "file": relative_path,
                "available": file_path.is_file()
            }

        return results

    def get_system_summary(self):
        statuses = self.get_agent_status()

        available = sum(
            1 for item in statuses.values()
            if item["available"]
        )

        total = len(statuses)

        summary = {
            "system": "LINKBUILD AI OS",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "total_agents": total,
            "available_agents": available,
            "missing_agents": total - available,
            "agents": statuses
        }

        self.log_event("SYSTEM_STATUS_CHECK", {
            "available_agents": available,
            "total_agents": total
        })

        return summary

    def save_workflow_event(self, workflow_name, status, details=None):
        self.log_event("WORKFLOW_EVENT", {
            "workflow": workflow_name,
            "status": status,
            "details": details or {}
        })

    def show_status(self):
        summary = self.get_system_summary()

        print("\n=== LINKBUILD AI OS | CENTRAL BRAIN ===")
        print(f"Total agents: {summary['total_agents']}")
        print(f"Available files: {summary['available_agents']}")
        print(f"Missing files: {summary['missing_agents']}")

        print("\n--- AGENT STATUS ---")

        for name, item in summary["agents"].items():
            status = "AVAILABLE" if item["available"] else "MISSING"
            print(f"{name}: {status}")

        print("\nStatus report completed.")
        print(f"Log file: {LOG_FILE}")


def main():
    brain = CentralBrain()
    brain.show_status()


if __name__ == "__main__":
    main()
