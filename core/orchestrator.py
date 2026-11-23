import json
import logging

from core.task_manager import (
    get_pending_tasks,
    update_task_status
)

logger = logging.getLogger("LINKBUILD_AI_OS.ORCHESTRATOR")


class Orchestrator:

    def __init__(self):
        self.agents = {}

    def register_agent(self, agent_name, handler):
        """
        Register an agent and its execution function.
        """
        if not callable(handler):
            raise TypeError("Agent handler must be callable")

        self.agents[agent_name] = handler

        logger.info("Agent registered: %s", agent_name)

    def list_agents(self):
        return list(self.agents.keys())

    def execute_task(self, task):
        task_id = task["id"]
        agent_name = task["agent_name"]

        handler = self.agents.get(agent_name)

        if handler is None:
            update_task_status(
                task_id,
                "FAILED",
                error=f"No handler registered for agent: {agent_name}"
            )

            logger.error("No handler found for %s", agent_name)
            return

        try:
            update_task_status(task_id, "RUNNING")

            input_data = json.loads(task.get("input_data") or "{}")

            result = handler(input_data)

            update_task_status(
                task_id,
                "COMPLETED",
                result=result
            )

            logger.info("Task %s completed", task_id)

        except Exception as error:
            update_task_status(
                task_id,
                "FAILED",
                error=str(error)
            )

            logger.exception("Task %s failed", task_id)

    def process_pending_tasks(self, limit=10):
        """
        Process pending tasks for registered agents.
        """
        tasks = get_pending_tasks(limit=limit)

        processed = 0

        for task in tasks:
            if task["agent_name"] not in self.agents:
                continue

            self.execute_task(task)
            processed += 1

        return {
            "found": len(tasks),
            "processed": processed,
            "registered_agents": self.list_agents()
        }