
from core.task_manager import create_task
from integrations.ai.ai_router import ai_router


def run_gemini_task(input_data):
    """
    Execute an AI task through Gemini.
    """

    prompt = input_data.get("prompt", "")

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("A valid prompt is required.")

    return ai_router.generate(
        prompt=prompt,
        provider="auto"
    )


def register_gemini_agent(orchestrator):
    """
    Register Gemini AI with the Central Brain.
    """

    orchestrator.register_agent(
        "gemini_agent",
        run_gemini_task
    )

    return orchestrator


def create_gemini_task(prompt):
    """
    Create a Gemini task in the shared database.
    """

    return create_task(
        task_name="Gemini AI Task",
        agent_name="gemini_agent",
        input_data={
            "prompt": prompt
        }
    )
