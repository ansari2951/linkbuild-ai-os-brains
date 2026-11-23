
from core.orchestrator import Orchestrator
from core.task_manager import create_task
from agents.seo.pipeline.agent_runner import run_all


def run_seo_task(input_data):
    """
    Execute SEO analysis through the Central Brain.
    """

    websites = input_data.get("websites", [])

    if isinstance(websites, str):
        websites = [websites]

    if not websites:
        raise ValueError("At least one website URL is required.")

    return run_all(websites)


def register_seo_agent(orchestrator):
    """
    Register SEO agent with the Central Orchestrator.
    """

    orchestrator.register_agent(
        "seo_agent",
        run_seo_task
    )

    return orchestrator


def create_seo_task(websites):
    """
    Create a new SEO task in the shared database.
    """

    return create_task(
        task_name="SEO Website Analysis",
        agent_name="seo_agent",
        input_data={
            "websites": websites
        }
    )
