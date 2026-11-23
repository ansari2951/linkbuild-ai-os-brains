
from core.task_manager.manager import (
    claim_next_task,
    recover_stale_tasks,
    update_task_status
)

from core.agent_runtime.dispatcher import execute_agent


def run_engine(limit=20):
    recovered = recover_stale_tasks()

    if recovered:
        print(f"\nRecovered interrupted tasks: {recovered}")

    summary = {
        "processed": 0,
        "completed": 0,
        "needs_input": 0,
        "failed": 0
    }

    print("\nExecution Engine Started")

    for _ in range(limit):
        task = claim_next_task()

        if task is None:
            break

        task_id = task["task_id"]
        agent_id = task["agent_id"]
        command = task["command"]

        print(f"\nExecuting Task: {task_id}")
        print(f"Agent: {agent_id}")

        try:
            result = execute_agent(agent_id, command)

            if not isinstance(result, dict):
                result = {
                    "status": "needs_input",
                    "message": "Unsupported agent result format."
                }

            status = result.get("status", "needs_input")

            if status not in {"completed", "needs_input", "failed"}:
                status = "needs_input"

            error_message = None

            if status == "failed":
                error_message = str(
                    result.get("message", "Agent execution failed.")
                )

            update_task_status(
                task_id,
                status,
                result=result,
                error=error_message
            )

            summary["processed"] += 1
            summary[status] += 1

            print(f"Task Result: {status}")

        except Exception as error:
            try:
                update_task_status(
                    task_id,
                    "failed",
                    error=str(error)
                )
            except Exception as database_error:
                print(f"Database Error: {database_error}")

            summary["processed"] += 1
            summary["failed"] += 1

            print(f"Task Error: {error}")

    print("\nEXECUTION SUMMARY")
    print("-" * 35)

    for key, value in summary.items():
        print(f"{key}: {value}")

    return summary
