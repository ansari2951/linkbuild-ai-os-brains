
from pathlib import Path
import argparse
import sys


PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_manual_pipeline():
    from agents.seo.pipeline.seo_pipeline import run_pipeline

    print("\nStarting LINKBUILD AI OS SEO Pipeline...")
    run_pipeline()


def run_scheduled_check():
    from agents.seo.pipeline.scheduled_runner import main

    print("\nChecking scheduled SEO pipeline...")
    main()


def show_project_info():
    print("\n===== LINKBUILD AI OS =====")
    print(f"Project location: {PROJECT_ROOT}")
    print("SEO Pipeline: Available")
    print("Execution mode: Local")
    print("Email sending: Not enabled by this launcher")


def main():
    parser = argparse.ArgumentParser(
        description="LINKBUILD AI OS SEO Pipeline Launcher"
    )

    parser.add_argument(
        "--mode",
        choices=["manual", "scheduled", "info"],
        default="manual",
        help="Choose pipeline execution mode"
    )

    args = parser.parse_args()

    try:
        if args.mode == "manual":
            run_manual_pipeline()

        elif args.mode == "scheduled":
            run_scheduled_check()

        elif args.mode == "info":
            show_project_info()

    except Exception as error:
        print(f"\nLauncher error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
