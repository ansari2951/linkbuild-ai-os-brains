
import csv
import re
import json
import dns.resolver
from pathlib import Path
from email_validator import validate_email, EmailNotValidError

ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = ROOT / "data" / "private" / "email_extraction" / "email_results.csv"

OUTPUT_DIR = ROOT / "data" / "private" / "email_extraction"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VALID_FILE = OUTPUT_DIR / "verified_emails.csv"
REPORT_FILE = OUTPUT_DIR / "validation_report.json"


def check_email(email):

    result = {
        "email": email,
        "syntax_valid": False,
        "domain": "",
        "mx_found": False,
        "status": "INVALID",
        "reason": ""
    }

    try:
        checked = validate_email(
            email,
            check_deliverability=False
        )

        domain = checked.domain

        result["syntax_valid"] = True
        result["domain"] = domain

    except EmailNotValidError as error:
        result["reason"] = str(error)
        return result

    try:
        dns.resolver.resolve(domain, "MX")

        result["mx_found"] = True
        result["status"] = "MX_FOUND"

    except dns.resolver.NXDOMAIN:
        result["status"] = "INVALID_DOMAIN"
        result["reason"] = "Domain does not exist"

    except dns.resolver.NoAnswer:
        result["status"] = "NO_MX"
        result["reason"] = "No MX record found"

    except dns.resolver.Timeout:
        result["status"] = "UNKNOWN"
        result["reason"] = "DNS timeout"

    except dns.resolver.NoNameservers:
        result["status"] = "UNKNOWN"
        result["reason"] = "DNS nameservers unavailable"

    except Exception as error:
        result["status"] = "UNKNOWN"
        result["reason"] = str(error)

    return result


def main():

    if not INPUT_FILE.exists():
        print("ERROR: Input CSV not found")
        return

    with open(INPUT_FILE, encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    unique = {}

    for row in rows:
        email = row.get("email", "").strip().lower()

        if email and email not in unique:
            unique[email] = row

    results = []

    print("=" * 50)
    print("LINKBUILD AI OS - EMAIL VALIDATOR")
    print("=" * 50)

    for index, email in enumerate(unique, 1):

        print(f"[{index}/{len(unique)}] Checking: {email}")

        result = check_email(email)

        result["website"] = unique[email]["website"]
        result["source_url"] = unique[email]["source_url"]

        results.append(result)

        print("STATUS:", result["status"])

    with open(VALID_FILE, "w", encoding="utf-8-sig", newline="") as file:

        fields = [
            "email",
            "website",
            "source_url",
            "syntax_valid",
            "domain",
            "mx_found",
            "status",
            "reason"
        ]

        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    summary = {
        "total": len(results),
        "mx_found": sum(r["status"] == "MX_FOUND" for r in results),
        "invalid": sum(r["status"] in ["INVALID", "INVALID_DOMAIN"] for r in results),
        "no_mx": sum(r["status"] == "NO_MX" for r in results),
        "unknown": sum(r["status"] == "UNKNOWN" for r in results)
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            {"summary": summary, "results": results},
            file,
            indent=4
        )

    print("\nVALIDATION COMPLETED")
    print(json.dumps(summary, indent=4))
    print("\nCSV:", VALID_FILE)
    print("REPORT:", REPORT_FILE)


if __name__ == "__main__":
    main()
