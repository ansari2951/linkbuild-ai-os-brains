
import csv
import ipaddress
import socket
from pathlib import Path
from urllib.parse import urlparse

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = PROJECT_ROOT / "data" / "private" / "seo" / "redirects"
OUTPUT_FILE = OUTPUT_DIR / "redirect_results.csv"

USER_AGENT = "LinkBuildAIOSBot/1.0"
TIMEOUT = 12
MAX_REDIRECTS = 10


def is_public_host(hostname):
    if not hostname or hostname.lower() == "localhost":
        return False

    try:
        addresses = socket.getaddrinfo(hostname, None)

        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])

            if not ip.is_global:
                return False

        return bool(addresses)

    except (socket.gaierror, ValueError):
        return False


def validate_url(url):
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are allowed.")

    if not parsed.hostname or not is_public_host(parsed.hostname):
        raise ValueError("Private or invalid host blocked.")

    return url


def analyze_redirect(start_url):
    current_url = validate_url(start_url.strip())

    visited = set()
    chain = []
    redirect_types = []
    final_url = current_url
    final_status = ""
    error = ""
    loop_detected = False

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    for step in range(MAX_REDIRECTS + 1):

        if current_url in visited:
            loop_detected = True
            error = "Redirect loop detected"
            break

        visited.add(current_url)

        try:
            # Check every destination before requesting it.
            validate_url(current_url)

            response = session.get(
                current_url,
                timeout=TIMEOUT,
                allow_redirects=False,
                stream=True
            )

            status = response.status_code
            location = response.headers.get("Location", "")

            record = {
                "step": step + 1,
                "url": current_url,
                "status_code": status,
                "redirect_location": location
            }

            chain.append(record)
            final_status = status
            final_url = current_url

            if status in (301, 302, 303, 307, 308):

                redirect_types.append(str(status))

                if not location:
                    error = "Redirect response without Location header"
                    response.close()
                    break

                next_url = requests.compat.urljoin(
                    current_url,
                    location
                )

                response.close()

                # Validate the destination before following it.
                current_url = validate_url(next_url)
                continue

            response.close()
            break

        except ValueError as exception:
            error = str(exception)
            break

        except requests.RequestException as exception:
            error = str(exception)
            break

    else:
        error = "Maximum redirect limit reached"

    redirect_chain = " -> ".join(
        item["url"] for item in chain
    )

    return {
        "start_url": start_url,
        "final_url": final_url,
        "final_status": final_status,
        "redirect_count": len(redirect_types),
        "redirect_types": ", ".join(redirect_types),
        "redirect_chain": redirect_chain,
        "loop_detected": loop_detected,
        "error": error
    }


def save_results(results):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not results:
        print("No results to save.")
        return

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys())
        )

        writer.writeheader()
        writer.writerows(results)

    print(f"Redirect report saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    website = input("Enter URL to analyze: ").strip()

    try:
        result = analyze_redirect(website)
        save_results([result])

        print("\nRedirect Analysis")
        print("Final URL:", result["final_url"])
        print("Redirect Count:", result["redirect_count"])
        print("Redirect Types:", result["redirect_types"])
        print("Loop Detected:", result["loop_detected"])

        if result["error"]:
            print("Issue:", result["error"])

    except Exception as error:
        print(f"Analysis failed: {error}")
