
import csv
import ipaddress
import socket
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = PROJECT_ROOT / "data" / "private" / "seo" / "images"
OUTPUT_FILE = OUTPUT_DIR / "image_audit.csv"

USER_AGENT = "LinkBuildAIOSBot/1.0"
TIMEOUT = 15
MAX_IMAGES = 300


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


def get_image_format(image_url):
    path = urlparse(image_url).path.lower()

    extensions = {
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".png": "PNG",
        ".webp": "WebP",
        ".gif": "GIF",
        ".svg": "SVG",
        ".avif": "AVIF",
        ".ico": "ICO"
    }

    for extension, image_format in extensions.items():
        if path.endswith(extension):
            return image_format

    return "Unknown"


def get_image_size(image_url):
    try:
        validate_url(image_url)

        response = requests.get(
            image_url,
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
            allow_redirects=False,
            stream=True
        )

        size = response.headers.get("Content-Length", "")
        content_type = response.headers.get("Content-Type", "")
        status = response.status_code

        response.close()

        return {
            "status": status,
            "size_bytes": size,
            "content_type": content_type
        }

    except Exception as error:
        return {
            "status": "ERROR",
            "size_bytes": "",
            "content_type": str(error)
        }


def analyze_images(page_url):
    validate_url(page_url)

    response = requests.get(
        page_url,
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
        allow_redirects=False
    )

    if response.status_code != 200:
        raise ValueError(
            f"Website returned HTTP {response.status_code}"
        )

    if "text/html" not in response.headers.get(
        "Content-Type", ""
    ).lower():
        raise ValueError("URL did not return HTML.")

    soup = BeautifulSoup(response.text, "html.parser")

    image_elements = soup.find_all("img")[:MAX_IMAGES]

    results = []

    for index, image in enumerate(image_elements, start=1):
        source = (
            image.get("src")
            or image.get("data-src")
            or image.get("data-lazy-src")
            or ""
        )

        if not source:
            continue

        image_url = urljoin(page_url, source)

        try:
            validate_url(image_url)
        except ValueError:
            continue

        alt = image.get("alt")
        width = image.get("width", "")
        height = image.get("height", "")

        if alt is None:
            alt_status = "MISSING"
        elif not alt.strip():
            alt_status = "EMPTY"
        else:
            alt_status = "PRESENT"

        lazy_loading = (
            image.get("loading", "").lower() == "lazy"
            or bool(image.get("data-src"))
            or bool(image.get("data-lazy-src"))
        )

        image_info = get_image_size(image_url)

        results.append({
            "page_url": page_url,
            "image_number": index,
            "image_url": image_url,
            "alt_text": alt or "",
            "alt_status": alt_status,
            "format": get_image_format(image_url),
            "size_bytes": image_info["size_bytes"],
            "http_status": image_info["status"],
            "content_type": image_info["content_type"],
            "lazy_loading": lazy_loading,
            "width": width,
            "height": height,
            "missing_dimensions": not bool(width and height)
        })

    return results


DEFAULT_IMAGE_FIELDS = [
    "page_url", "image_number", "image_url", "alt_text", "alt_status",
    "format", "size_bytes", "http_status", "content_type",
    "lazy_loading", "width", "height", "missing_dimensions"
]


def save_results(results):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = list(results[0].keys()) if results else DEFAULT_IMAGE_FIELDS

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        if results:
            writer.writerows(results)

    if not results:
        print("No images found. Empty report saved.")
    else:
        print(f"Image audit saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    website = input("Enter website page URL: ").strip()

    try:
        results = analyze_images(website)
        save_results(results)

        print("\nImage Audit Summary")
        print("Total images:", len(results))
        print(
            "Missing ALT:",
            sum(1 for item in results
                if item["alt_status"] == "MISSING")
        )
        print(
            "Empty ALT:",
            sum(1 for item in results
                if item["alt_status"] == "EMPTY")
        )
        print(
            "Missing dimensions:",
            sum(1 for item in results
                if item["missing_dimensions"])
        )

    except Exception as error:
        print(f"Analysis failed: {error}")
