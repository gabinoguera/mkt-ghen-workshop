#!/usr/bin/env python3
"""SERP scraping and SEO metrics analyzer for af_seo.

CLI tool for scraping competitor pages and extracting SEO metrics.
Used by the seo-strategist agent.

Usage:
    python serp_analyzer.py scrape --url "https://example.com/page"
    python serp_analyzer.py batch --urls-file urls.txt [--output-dir results/]
    python serp_analyzer.py metrics --file scraped.json
    python serp_analyzer.py analyze --url "https://example.com/page"
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Comment

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

REQUEST_TIMEOUT = 20
BATCH_DELAY = 2  # seconds between requests


# --- Scraping ---

def scrape_url(url: str) -> dict:
    """Scrape a single URL and return structured data."""
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        status_code = resp.status_code
        final_url = resp.url
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "error": str(e),
            "status_code": getattr(getattr(e, "response", None), "status_code", None),
        }

    soup = BeautifulSoup(resp.text, "lxml")

    data = {
        "url": url,
        "final_url": final_url,
        "status_code": status_code,
        "title": _extract_title(soup),
        "meta_description": _extract_meta_description(soup),
        "lang": _extract_lang(soup),
        "canonical": _extract_canonical(soup),
        "headings": _extract_headings(soup),
        "content_text": _extract_content_text(soup),
        "word_count": 0,  # calculated below
        "internal_links": [],
        "external_links": [],
        "images": _extract_images(soup, url),
        "schema_types": _extract_schema_types(soup),
    }

    # Word count from extracted content
    data["word_count"] = len(data["content_text"].split()) if data["content_text"] else 0

    # Links
    internal, external = _extract_links(soup, url)
    data["internal_links"] = internal
    data["external_links"] = external

    return data


def _extract_title(soup: BeautifulSoup) -> str:
    tag = soup.find("title")
    return tag.get_text().strip() if tag else ""


def _extract_meta_description(soup: BeautifulSoup) -> str:
    tag = soup.find("meta", attrs={"name": "description"})
    return tag.get("content", "").strip() if tag else ""


def _extract_lang(soup: BeautifulSoup) -> str:
    html_tag = soup.find("html")
    if html_tag:
        return html_tag.get("lang", "")
    return ""


def _extract_canonical(soup: BeautifulSoup) -> str:
    tag = soup.find("link", attrs={"rel": "canonical"})
    return tag.get("href", "") if tag else ""


def _extract_headings(soup: BeautifulSoup) -> list[dict]:
    """Extract all headings with level and text."""
    headings = []
    for tag in soup.find_all(re.compile(r"^h[1-6]$")):
        level = int(tag.name[1])
        text = tag.get_text().strip()
        if text:
            headings.append({"level": level, "text": text})
    return headings


def _extract_content_text(soup: BeautifulSoup) -> str:
    """Extract main content text, prioritizing article/main elements."""
    # Remove script, style, nav, footer, header, aside
    for tag in soup.find_all(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()

    # Remove HTML comments
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    # Try to find main content area
    main_content = (
        soup.find("article")
        or soup.find("main")
        or soup.find(attrs={"role": "main"})
        or soup.find(attrs={"id": re.compile(r"content|main|article", re.I)})
        or soup.find(attrs={"class": re.compile(r"content|main|article|entry", re.I)})
    )

    target = main_content if main_content else soup.body
    if not target:
        return ""

    text = target.get_text(separator=" ", strip=True)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_links(soup: BeautifulSoup, base_url: str) -> tuple[list[dict], list[dict]]:
    """Extract internal and external links with anchor text."""
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc.lower()
    internal = []
    external = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue

        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        anchor = a_tag.get_text().strip()

        link_data = {"url": full_url, "anchor": anchor}

        if parsed.netloc.lower() == base_domain:
            internal.append(link_data)
        else:
            external.append(link_data)

    return internal, external


def _extract_images(soup: BeautifulSoup, base_url: str) -> list[dict]:
    """Extract images with src and alt text presence."""
    images = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src:
            continue
        images.append({
            "src": urljoin(base_url, src),
            "alt": img.get("alt", ""),
            "has_alt": bool(img.get("alt", "").strip()),
        })
    return images


def _extract_schema_types(soup: BeautifulSoup) -> list[str]:
    """Extract schema.org types from JSON-LD blocks."""
    types = set()
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string)
            _collect_schema_types(data, types)
        except (json.JSONDecodeError, TypeError):
            continue
    return sorted(types)


def _collect_schema_types(data, types: set):
    """Recursively collect @type values from JSON-LD."""
    if isinstance(data, dict):
        if "@type" in data:
            t = data["@type"]
            if isinstance(t, list):
                types.update(t)
            else:
                types.add(t)
        # Check @graph
        if "@graph" in data:
            _collect_schema_types(data["@graph"], types)
        for v in data.values():
            if isinstance(v, (dict, list)):
                _collect_schema_types(v, types)
    elif isinstance(data, list):
        for item in data:
            _collect_schema_types(item, types)


# --- Metrics ---

def compute_metrics(scraped: dict) -> dict:
    """Compute SEO metrics from scraped data."""
    if "error" in scraped:
        return {"url": scraped["url"], "error": scraped["error"]}

    title = scraped.get("title", "")
    meta_desc = scraped.get("meta_description", "")
    headings = scraped.get("headings", [])

    # Heading outline
    outline = []
    for h in headings:
        indent = "  " * (h["level"] - 1)
        outline.append(f"{indent}H{h['level']}: {h['text']}")

    # Heading hierarchy validation
    heading_issues = _validate_heading_hierarchy(headings)

    # Link counts
    internal_links = scraped.get("internal_links", [])
    external_links = scraped.get("external_links", [])

    # Image alt coverage
    images = scraped.get("images", [])
    images_with_alt = sum(1 for img in images if img.get("has_alt"))

    return {
        "url": scraped.get("url", ""),
        "status_code": scraped.get("status_code"),
        "title": title,
        "title_length": len(title),
        "meta_description": meta_desc,
        "meta_description_length": len(meta_desc),
        "lang": scraped.get("lang", ""),
        "canonical": scraped.get("canonical", ""),
        "word_count": scraped.get("word_count", 0),
        "heading_count": len(headings),
        "heading_outline": outline,
        "heading_issues": heading_issues,
        "internal_link_count": len(internal_links),
        "external_link_count": len(external_links),
        "image_count": len(images),
        "images_with_alt": images_with_alt,
        "images_missing_alt": len(images) - images_with_alt,
        "schema_types": scraped.get("schema_types", []),
    }


def _validate_heading_hierarchy(headings: list[dict]) -> list[str]:
    """Check heading hierarchy for common issues."""
    issues = []
    h1_count = sum(1 for h in headings if h["level"] == 1)

    if h1_count == 0:
        issues.append("No H1 found")
    elif h1_count > 1:
        issues.append(f"Multiple H1 tags found ({h1_count})")

    # Check for level skips (e.g., H2 → H4 without H3)
    prev_level = 0
    for h in headings:
        if prev_level > 0 and h["level"] > prev_level + 1:
            issues.append(f"Heading skip: H{prev_level} → H{h['level']} (missing H{prev_level + 1})")
        prev_level = h["level"]

    return issues


# --- Subcommands ---

def cmd_scrape(args):
    """Scrape a single URL."""
    data = scrape_url(args.url)
    if args.output:
        Path(args.output).write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(json.dumps({"saved": args.output, "url": args.url}, ensure_ascii=False))
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_batch(args):
    """Scrape multiple URLs from a file."""
    urls_file = Path(args.urls_file)
    if not urls_file.exists():
        _error_exit(f"File not found: {urls_file}")

    urls = [
        line.strip()
        for line in urls_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    if not urls:
        _error_exit("No URLs found in file")

    output_dir = Path(args.output_dir) if args.output_dir else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for i, url in enumerate(urls):
        print(f"[{i + 1}/{len(urls)}] Scraping: {url}", file=sys.stderr)
        data = scrape_url(url)
        results.append(data)

        if output_dir:
            slug = urlparse(url).netloc + urlparse(url).path.rstrip("/")
            slug = re.sub(r"[^a-zA-Z0-9]+", "_", slug).strip("_")
            out_file = output_dir / f"{slug}.json"
            out_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        if i < len(urls) - 1:
            time.sleep(BATCH_DELAY)

    summary = {
        "action": "batch",
        "total": len(urls),
        "success": sum(1 for r in results if "error" not in r),
        "errors": sum(1 for r in results if "error" in r),
    }
    if output_dir:
        summary["output_dir"] = str(output_dir)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


def cmd_metrics(args):
    """Compute metrics from a scraped JSON file."""
    file_path = Path(args.file)
    if not file_path.exists():
        _error_exit(f"File not found: {file_path}")

    data = json.loads(file_path.read_text(encoding="utf-8"))
    metrics = compute_metrics(data)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


def cmd_analyze(args):
    """Scrape + compute metrics in one step."""
    data = scrape_url(args.url)
    metrics = compute_metrics(data)

    output = {
        "scrape": data,
        "metrics": metrics,
    }

    if args.output:
        Path(args.output).write_text(
            json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(json.dumps({"saved": args.output, "url": args.url}, ensure_ascii=False))
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))


# --- Helpers ---

def _error_exit(message: str, code: int = 1):
    print(json.dumps({"error": message}, ensure_ascii=False), file=sys.stderr)
    sys.exit(code)


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(
        description="SERP scraping and SEO metrics analyzer for af_seo"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # scrape
    p_scrape = subparsers.add_parser("scrape", help="Scrape a single URL")
    p_scrape.add_argument("--url", required=True, help="URL to scrape")
    p_scrape.add_argument("--output", "-o", help="Save output to file")
    p_scrape.set_defaults(func=cmd_scrape)

    # batch
    p_batch = subparsers.add_parser("batch", help="Scrape multiple URLs from a file")
    p_batch.add_argument("--urls-file", required=True, help="File with one URL per line")
    p_batch.add_argument("--output-dir", help="Directory to save individual results")
    p_batch.set_defaults(func=cmd_batch)

    # metrics
    p_metrics = subparsers.add_parser("metrics", help="Compute SEO metrics from scraped JSON")
    p_metrics.add_argument("--file", required=True, help="Path to scraped JSON file")
    p_metrics.set_defaults(func=cmd_metrics)

    # analyze
    p_analyze = subparsers.add_parser("analyze", help="Scrape + metrics in one step")
    p_analyze.add_argument("--url", required=True, help="URL to analyze")
    p_analyze.add_argument("--output", "-o", help="Save output to file")
    p_analyze.set_defaults(func=cmd_analyze)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
