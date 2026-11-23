import json
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[1]

WORKFLOW_DIR = PROJECT_ROOT / "data" / "private" / "workflows"
WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)

WORKFLOW_FILE = WORKFLOW_DIR / "workflow_history.json"


class WorkflowManager:

    def __init__(self):
        self.workflows = self._load_workflows()

    def _load_workflows(self):
        if not WORKFLOW_FILE.exists():
            return []

        try:
            with open(WORKFLOW_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return []

    def _save_workflows(self):
        with open(WORKFLOW_FILE, "w", encoding="utf-8") as file:
            json.dump(self.workflows, file, indent=4)

    def create_workflow(self, name, steps):
        workflow = {
            "id": f"WF-{len(self.workflows) + 1:05d}",
            "name": name,
            "steps": [
                {
                    "name": step,
                    "status": "PENDING"
                }
                for step in steps
            ],
            "status": "CREATED",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        self.workflows.append(workflow)
        self._save_workflows()

        return workflow

    def update_step(self, workflow_id, step_name, status):
        allowed_statuses = {
            "PENDING",
            "RUNNING",
            "COMPLETED",
            "FAILED",
            "SKIPPED"
        }

        if status not in allowed_statuses:
            raise ValueError("Invalid workflow step status")

        for workflow in self.workflows:
            if workflow["id"] == workflow_id:

                for step in workflow["steps"]:
                    if step["name"] == step_name:
                        step["status"] = status

                        statuses = [
                            item["status"]
                            for item in workflow["steps"]
                        ]

                        if "FAILED" in statuses:
                            workflow["status"] = "FAILED"
                        elif all(s == "COMPLETED" for s in statuses):
                            workflow["status"] = "COMPLETED"
                        else:
                            workflow["status"] = "IN_PROGRESS"

                        self._save_workflows()
                        return workflow

        raise ValueError("Workflow or step not found")

    def get_all_workflows(self):
        return self.workflows

    def get_workflow(self, workflow_id):
        for workflow in self.workflows:
            if workflow["id"] == workflow_id:
                return workflow

        return None