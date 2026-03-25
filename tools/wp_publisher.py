#!/usr/bin/env python3
"""WordPress REST API publisher for af_seo.

CLI tool for publishing content to archivofinal.com via WP REST API.
Used by the wp-implementer agent.

Usage:
    python wp_publisher.py publish --file post.md --title "My Post" [--status draft]
    python wp_publisher.py publish --file page.html --title "FAQ" --type page --slug preguntas-frecuentes --raw
    python wp_publisher.py upload-image --file image.jpg [--alt-text "Description"]
    python wp_publisher.py list-categories
    python wp_publisher.py list-tags
    python wp_publisher.py get-post --post-id 123
    python wp_publisher.py update --post-id 123 [--file post.md] [--title "New Title"]
"""

import argparse
import base64
import json
import mimetypes
import re
import sys
from pathlib import Path

import markdown
import requests
from bs4 import BeautifulSoup

from config import WP_API_URL, WP_BASE_URL, get_wp_auth


# --- Markdown to HTML conversion ---

MD_EXTENSIONS = ["extra", "smarty", "toc", "tables", "fenced_code"]


def md_to_html(md_text: str) -> str:
    """Convert Markdown to clean HTML suitable for WordPress."""
    html = markdown.markdown(md_text, extensions=MD_EXTENSIONS)
    html = _demote_h1_to_h2(html)
    html = _clean_html(html)
    return html


def _demote_h1_to_h2(html: str) -> str:
    """Demote H1 to H2 since WP post title is already H1."""
    html = re.sub(r"<h1([\s>])", r"<h2\1", html)
    html = re.sub(r"</h1>", "</h2>", html)
    return html


def _clean_html(html: str) -> str:
    """Remove empty paragraphs and reduce excessive blank lines."""
    html = re.sub(r"<p>\s*</p>", "", html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()


# --- Category/Tag resolution ---

def resolve_category_id(name: str, auth: tuple) -> int | None:
    """Resolve category name to ID. Returns None if not found."""
    resp = requests.get(
        f"{WP_API_URL}/categories",
        params={"search": name, "per_page": 100},
        auth=auth,
        timeout=15,
    )
    resp.raise_for_status()
    for cat in resp.json():
        if cat["name"].lower() == name.lower():
            return cat["id"]
    return None


def resolve_tag_id(name: str, auth: tuple, create: bool = True) -> int | None:
    """Resolve tag name to ID. Optionally creates the tag if not found."""
    resp = requests.get(
        f"{WP_API_URL}/tags",
        params={"search": name, "per_page": 100},
        auth=auth,
        timeout=15,
    )
    resp.raise_for_status()
    for tag in resp.json():
        if tag["name"].lower() == name.lower():
            return tag["id"]
    if create:
        resp = requests.post(
            f"{WP_API_URL}/tags",
            json={"name": name},
            auth=auth,
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()["id"]
    return None


# --- Subcommands ---

def cmd_publish(args):
    """Publish a Markdown file as a WordPress post or page."""
    auth = get_wp_auth()
    file_path = Path(args.file)
    if not file_path.exists():
        _error_exit(f"File not found: {file_path}")

    raw_text = file_path.read_text(encoding="utf-8")
    html_content = raw_text if args.raw else md_to_html(raw_text)

    # Determine endpoint based on content type
    content_type = args.type  # "post" or "page"
    endpoint = f"{WP_API_URL}/{'pages' if content_type == 'page' else 'posts'}"

    post_data = {
        "title": args.title,
        "content": html_content,
        "status": args.status,
    }

    # Custom slug
    if args.slug:
        post_data["slug"] = args.slug

    # Category resolution (posts only)
    if args.category and content_type == "post":
        cat_id = resolve_category_id(args.category, auth)
        if cat_id is None:
            _error_exit(f"Category not found: {args.category}")
        post_data["categories"] = [cat_id]

    # Tags resolution (posts only)
    if args.tags and content_type == "post":
        tag_ids = []
        for tag_name in args.tags.split(","):
            tag_name = tag_name.strip()
            if tag_name:
                tag_id = resolve_tag_id(tag_name, auth, create=True)
                if tag_id:
                    tag_ids.append(tag_id)
        if tag_ids:
            post_data["tags"] = tag_ids

    # Featured image: upload first, then attach
    featured_media_id = None
    if args.featured_image:
        img_path = Path(args.featured_image)
        if not img_path.exists():
            _error_exit(f"Image file not found: {img_path}")
        featured_media_id = _upload_media(img_path, auth, alt_text=args.title)
        post_data["featured_media"] = featured_media_id

    # Rank Math SEO meta (requires register_post_meta snippet in functions.php)
    meta = {}
    if args.seo_title:
        meta["rank_math_title"] = args.seo_title
    if args.seo_description:
        meta["rank_math_description"] = args.seo_description
    if args.focus_keyword:
        meta["rank_math_focus_keyword"] = args.focus_keyword
    if meta:
        post_data["meta"] = meta

    resp = requests.post(
        endpoint,
        json=post_data,
        auth=auth,
        timeout=30,
    )
    resp.raise_for_status()
    post = resp.json()

    result = {
        "action": "publish",
        "type": content_type,
        "post_id": post["id"],
        "post_url": post["link"],
        "status": post["status"],
        "title": post["title"]["rendered"],
    }
    if args.slug:
        result["slug"] = post.get("slug", args.slug)
    if featured_media_id:
        result["featured_media_id"] = featured_media_id
    if meta:
        result["seo_meta"] = meta

    _json_output(result)


def cmd_upload_image(args):
    """Upload an image to the WordPress Media Library."""
    auth = get_wp_auth()
    img_path = Path(args.file)
    if not img_path.exists():
        _error_exit(f"File not found: {img_path}")

    media_id = _upload_media(img_path, auth, alt_text=args.alt_text or "")
    _json_output({
        "action": "upload-image",
        "media_id": media_id,
        "file": str(img_path),
    })


def _upload_media(file_path: Path, auth: tuple, alt_text: str = "") -> int:
    """Upload a file to WP Media Library and return the media ID."""
    mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"

    with open(file_path, "rb") as f:
        resp = requests.post(
            f"{WP_API_URL}/media",
            headers={
                "Content-Disposition": f'attachment; filename="{file_path.name}"',
                "Content-Type": mime_type,
            },
            data=f,
            auth=auth,
            timeout=60,
        )
    resp.raise_for_status()
    media = resp.json()

    # Set alt text if provided
    if alt_text:
        requests.post(
            f"{WP_API_URL}/media/{media['id']}",
            json={"alt_text": alt_text},
            auth=auth,
            timeout=15,
        )

    return media["id"]


def cmd_list_categories(args):
    """List all WordPress categories."""
    auth = get_wp_auth()
    categories = []
    page = 1
    while True:
        resp = requests.get(
            f"{WP_API_URL}/categories",
            params={"per_page": 100, "page": page},
            auth=auth,
            timeout=15,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        categories.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    result = [
        {"id": c["id"], "name": c["name"], "slug": c["slug"], "count": c["count"]}
        for c in categories
    ]
    _json_output({"action": "list-categories", "categories": result})


def cmd_list_tags(args):
    """List all WordPress tags."""
    auth = get_wp_auth()
    tags = []
    page = 1
    while True:
        resp = requests.get(
            f"{WP_API_URL}/tags",
            params={"per_page": 100, "page": page},
            auth=auth,
            timeout=15,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        tags.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    result = [
        {"id": t["id"], "name": t["name"], "slug": t["slug"], "count": t["count"]}
        for t in tags
    ]
    _json_output({"action": "list-tags", "tags": result})


def cmd_get_post(args):
    """Get details of a single post."""
    auth = get_wp_auth()
    resp = requests.get(
        f"{WP_API_URL}/posts/{args.post_id}",
        auth=auth,
        timeout=15,
    )
    resp.raise_for_status()
    post = resp.json()

    _json_output({
        "action": "get-post",
        "post_id": post["id"],
        "title": post["title"]["rendered"],
        "status": post["status"],
        "post_url": post["link"],
        "date": post["date"],
        "modified": post["modified"],
        "categories": post["categories"],
        "tags": post["tags"],
        "excerpt": BeautifulSoup(post["excerpt"]["rendered"], "html.parser").get_text().strip(),
        "word_count": len(BeautifulSoup(post["content"]["rendered"], "html.parser").get_text().split()),
    })


def cmd_update(args):
    """Update an existing post."""
    auth = get_wp_auth()
    update_data = {}

    if args.title:
        update_data["title"] = args.title
    if args.status:
        update_data["status"] = args.status
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            _error_exit(f"File not found: {file_path}")
        md_text = file_path.read_text(encoding="utf-8")
        update_data["content"] = md_to_html(md_text)

    # Rank Math SEO meta
    meta = {}
    if args.seo_title:
        meta["rank_math_title"] = args.seo_title
    if args.seo_description:
        meta["rank_math_description"] = args.seo_description
    if args.focus_keyword:
        meta["rank_math_focus_keyword"] = args.focus_keyword
    if meta:
        update_data["meta"] = meta

    if not update_data:
        _error_exit("No update fields provided")

    resp = requests.post(
        f"{WP_API_URL}/posts/{args.post_id}",
        json=update_data,
        auth=auth,
        timeout=30,
    )
    resp.raise_for_status()
    post = resp.json()

    result = {
        "action": "update",
        "post_id": post["id"],
        "post_url": post["link"],
        "status": post["status"],
        "title": post["title"]["rendered"],
    }
    if meta:
        result["seo_meta"] = meta
    _json_output(result)


# --- Helpers ---

def _json_output(data: dict):
    """Print JSON to stdout."""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _error_exit(message: str, code: int = 1):
    """Print error as JSON to stderr and exit."""
    print(json.dumps({"error": message}, ensure_ascii=False), file=sys.stderr)
    sys.exit(code)


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(
        description="WordPress REST API publisher for af_seo"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # publish
    p_pub = subparsers.add_parser("publish", help="Publish a Markdown file as a WP post or page")
    p_pub.add_argument("--file", required=True, help="Path to content file (Markdown or raw HTML)")
    p_pub.add_argument("--title", required=True, help="Post/page title")
    p_pub.add_argument("--type", default="post", choices=["post", "page"], help="Content type (default: post)")
    p_pub.add_argument("--slug", help="Custom URL slug")
    p_pub.add_argument("--raw", action="store_true", help="Skip Markdown conversion (use raw HTML content)")
    p_pub.add_argument("--status", default="draft", choices=["draft", "publish", "pending", "private"], help="Post status (default: draft)")
    p_pub.add_argument("--category", help="Category name (resolved to ID, posts only)")
    p_pub.add_argument("--tags", help="Comma-separated tag names (posts only)")
    p_pub.add_argument("--seo-title", dest="seo_title", help="Rank Math SEO title")
    p_pub.add_argument("--seo-description", dest="seo_description", help="Rank Math meta description")
    p_pub.add_argument("--focus-keyword", dest="focus_keyword", help="Rank Math focus keyword")
    p_pub.add_argument("--featured-image", dest="featured_image", help="Path to featured image")
    p_pub.set_defaults(func=cmd_publish)

    # upload-image
    p_img = subparsers.add_parser("upload-image", help="Upload image to Media Library")
    p_img.add_argument("--file", required=True, help="Path to image file")
    p_img.add_argument("--alt-text", dest="alt_text", help="Alt text for the image")
    p_img.set_defaults(func=cmd_upload_image)

    # list-categories
    p_cats = subparsers.add_parser("list-categories", help="List WordPress categories")
    p_cats.set_defaults(func=cmd_list_categories)

    # list-tags
    p_tags = subparsers.add_parser("list-tags", help="List WordPress tags")
    p_tags.set_defaults(func=cmd_list_tags)

    # get-post
    p_get = subparsers.add_parser("get-post", help="Get post details")
    p_get.add_argument("--post-id", required=True, type=int, help="Post ID")
    p_get.set_defaults(func=cmd_get_post)

    # update
    p_upd = subparsers.add_parser("update", help="Update an existing post")
    p_upd.add_argument("--post-id", required=True, type=int, help="Post ID to update")
    p_upd.add_argument("--file", help="Path to new Markdown content")
    p_upd.add_argument("--title", help="New title")
    p_upd.add_argument("--status", choices=["draft", "publish", "pending", "private"], help="New status")
    p_upd.add_argument("--seo-title", dest="seo_title", help="Rank Math SEO title")
    p_upd.add_argument("--seo-description", dest="seo_description", help="Rank Math meta description")
    p_upd.add_argument("--focus-keyword", dest="focus_keyword", help="Rank Math focus keyword")
    p_upd.set_defaults(func=cmd_update)

    args = parser.parse_args()
    try:
        args.func(args)
    except requests.exceptions.ConnectionError:
        _error_exit(f"Cannot connect to {WP_BASE_URL}")
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "unknown"
        body = ""
        if e.response is not None:
            try:
                body = e.response.json().get("message", "")
            except (ValueError, AttributeError):
                body = e.response.text[:200]
        _error_exit(f"HTTP {status}: {body}")


if __name__ == "__main__":
    main()
