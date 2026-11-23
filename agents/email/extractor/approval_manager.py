
import csv
import os
from datetime import datetime

BASE_DIR = os.path.join(
    "data",
    "private",
    "email_extraction"
)

INPUT_FILE = os.path.join(BASE_DIR, "outreach_drafts.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "approval_decisions.csv")


def main():
    if not os.path.exists(INPUT_FILE):
        print("ERROR: outreach_drafts.csv file nahi mili.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        drafts = list(reader)
        fieldnames = reader.fieldnames or []

    required_fields = [
        "email", "website", "contact_type",
        "priority", "subject", "body"
    ]

    missing = [field for field in required_fields if field not in fieldnames]

    if missing:
        print("ERROR: CSV mein ye columns missing hain:", missing)
        return

    if not drafts:
        print("Abhi koi outreach draft available nahi.")
        return

    decisions = []

    print("\nEMAIL APPROVAL SYSTEM")
    print("A = Approve | R = Reject | S = Skip | Q = Quit\n")

    for index, draft in enumerate(drafts, start=1):
        print("\n" + "=" * 60)
        print(f"Draft {index} of {len(drafts)}")
        print("Website:", draft["website"])
        print("Email:", draft["email"])
        print("Contact Type:", draft["contact_type"])
        print("Priority:", draft["priority"])
        print("Subject:", draft["subject"])
        print("\nEmail Body:\n")
        print(draft["body"])
        print("\n" + "=" * 60)

        while True:
            choice = input("Decision (A/R/S/Q): ").strip().upper()

            if choice in ["A", "R", "S", "Q"]:
                break

            print("Please A, R, S ya Q enter karo.")

        if choice == "Q":
            print("Review stopped.")
            break

        if choice == "A":
            decision = "APPROVED"
        elif choice == "R":
            decision = "REJECTED"
        else:
            decision = "SKIPPED"

        result = draft.copy()
        result["decision"] = decision
        result["decision_timestamp"] = datetime.now().isoformat(timespec="seconds")
        decisions.append(result)

        print("Saved decision:", decision)

    output_fields = fieldnames + ["decision", "decision_timestamp"]

    with open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(decisions)

    print("\nReview session complete.")
    print("Reviewed:", len(decisions))
    print("Approved:", sum(1 for d in decisions if d["decision"] == "APPROVED"))
    print("Rejected:", sum(1 for d in decisions if d["decision"] == "REJECTED"))
    print("Skipped:", sum(1 for d in decisions if d["decision"] == "SKIPPED"))
    print("\nDecisions saved to:", OUTPUT_FILE)
    print("Note: Approved ka matlab sirf review approval hai. Email send nahi hui.")


if __name__ == "__main__":
    main()
