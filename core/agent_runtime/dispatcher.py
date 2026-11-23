
from core.master_brain.registry import get_agent
from agents.publisher.research.brain import research_publisher


AGENT_HANDLERS = {
    "publisher_research": research_publisher
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
