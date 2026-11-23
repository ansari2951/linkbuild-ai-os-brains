
from core.master_brain.config import APP_NAME, APP_VERSION
from core.master_brain.registry import (
    list_agents,
    get_agent,
    get_agent_count
)
from core.master_brain.router import route_task
from core.task_manager.manager import create_task
from core.task_manager.executor import run_engine


def show_agents():
    print("\nREGISTERED AI AGENTS")
    print("-" * 45)

    for agent_id, agent in list_agents().items():
        print(
            f"{agent_id}: {agent['name']} "
            f"[{agent['status']}]"
        )

    print("-" * 45)
    print(f"Total registered agents: {get_agent_count()}")


def process_command(command):
    agent_id = route_task(command)

    if agent_id is None:
        print("\nMaster Brain: I could not identify the correct agent.")
        print("Please provide a more specific command.")
        return None

    agent = get_agent(agent_id)

    if agent is None:
        print("\nMaster Brain: Agent registration not found.")
        return None

    task = create_task(command, agent_id)

    print("\nTASK CREATED")
    print("-" * 40)
    print(f"Task ID: {task['task_id']}")
    print(f"Agent: {agent['name']}")
    print(f"Department: {agent['department']}")
    print(f"Status: {task['status']}")

    print("\nStarting execution engine...")

    summary = run_engine(limit=20)

    print("\nMaster Brain: Task processing finished.")
    return {
        "task": task,
        "execution_summary": summary
    }


def main():
    print(f"\n{APP_NAME} v{APP_VERSION}")
    print("MASTER BRAIN INITIALIZED")

    show_agents()

    print("\nType 'agents' to view agents.")
    print("Type 'exit' to close Master Brain.")

    while True:
        try:
            command = input("\nYou > ").strip()

            if command.lower() in ("exit", "quit"):
                print("Master Brain stopped.")
                break

            if command.lower() == "agents":
                show_agents()
                continue

            if command:
                process_command(command)

        except KeyboardInterrupt:
            print("\nMaster Brain stopped.")
            break

        except Exception as error:
            print(f"\nSystem error: {error}")


if __name__ == "__main__":
    main()
