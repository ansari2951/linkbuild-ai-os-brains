from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REGISTRY_DIR = PROJECT_ROOT / "data" / "private" / "system"
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

REGISTRY_FILE = REGISTRY_DIR / "agent_registry.json"


DEFAULT_AGENTS = [
    {
        "name": "Email Extractor",
        "category": "Email",
        "file": "agents/email/extractor/engine.py",
        "description": "Extract contact emails from websites"
    },
    {
        "name": "Email Validator",
        "category": "Email",
        "file": "agents/email/extractor/validator.py",
        "description": "Validate email syntax and domain MX records"
    },
    {
        "name": "Email Classifier",
        "category": "Email",
        "file": "agents/email/extractor/classifier.py",
        "description": "Classify extracted email addresses"
    },
    {
        "name": "Contact Intelligence",
        "category": "Email",
        "file": "agents/email/extractor/intelligence.py",
        "description": "Prioritize publisher contacts"
    },
    {
        "name": "Outreach Generator",
        "category": "Outreach",
        "file": "agents/email/extractor/outreach_generator.py",
        "description": "Generate outreach drafts"
    },
    {
        "name": "Email Personalizer",
        "category": "Outreach",
        "file": "agents/email/personalizer/personalizer.py",
        "description": "Personalize outreach drafts"
    },
    {
        "name": "Reply Detector",
        "category": "Outreach",
        "file": "agents/email/reply_detector/reply_detector.py",
        "description": "Classify publisher replies"
    },
    {
        "name": "Negotiation Agent",
        "category": "Publisher",
        "file": "agents/email/negotiation/negotiation.py",
        "description": "Prepare price negotiation drafts"
    },
    {
        "name": "Publisher CRM",
        "category": "Publisher",
        "file": "agents/publisher/crm/publisher_crm.py",
        "description": "Manage publisher records"
    },
    {
        "name": "Website Discovery",
        "category": "Research",
        "file": "agents/publisher/discovery/website_discovery.py",
        "description": "Organize discovered websites"
    },
    {
        "name": "Client Prospecting",
        "category": "Clients",
        "file": "agents/clients/prospecting/client_prospecting.py",
        "description": "Organize potential clients"
    }
]


class AgentRegistry:

    def __init__(self):
        self.agents = self._load()

    def _load(self):
        if REGISTRY_FILE.exists():
            try:
                with open(REGISTRY_FILE, "r", encoding="utf-8") as file:
                    return json.load(file)
            except (json.JSONDecodeError, OSError):
                pass

        self._save(DEFAULT_AGENTS)
        return DEFAULT_AGENTS.copy()

    def _save(self, agents=None):
        data = agents if agents is not None else self.agents

        with open(REGISTRY_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def get_all(self):
        results = []

        for agent in self.agents:
            item = agent.copy()
            path = PROJECT_ROOT / item["file"]
            item["file_exists"] = path.is_file()
            results.append(item)

        return results

    def get_by_category(self, category):
        return [
            agent for agent in self.get_all()
            if agent["category"].lower() == category.lower()
        ]

    def register(self, name, category, file, description=""):
        if any(agent["name"].lower() == name.lower()
               for agent in self.agents):
            raise ValueError("Agent already registered")

        agent = {
            "name": name,
            "category": category,
            "file": file,
            "description": description
        }

        self.agents.append(agent)
        self._save()

        return agent