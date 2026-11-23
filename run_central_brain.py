
from core.orchestrator import Orchestrator
from core.integrations.seo_integration import register_seo_agent
from core.integrations.ai_integration import register_gemini_agent


def main():
    print("=" * 50)
    print("LINKBUILD AI OS - CENTRAL BRAIN")
    print("=" * 50)

    orchestrator = Orchestrator()

    register_seo_agent(orchestrator)
    register_gemini_agent(orchestrator)

    print("\nRegistered Agents:")
    for agent in orchestrator.list_agents():
        print(f"- {agent}")

    print("\nProcessing pending tasks...")

    result = orchestrator.process_pending_tasks(limit=10)

    print("\nExecution Summary:")
    print(f"Tasks Found: {result['found']}")
    print(f"Tasks Processed: {result['processed']}")

    print("\nCentral Brain execution finished.")


if __name__ == "__main__":
    main()
