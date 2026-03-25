#!/usr/bin/env python3
"""Content QA checker for af_seo.

Mechanical quality checks on Markdown content before publishing.
Used by the marketing-copywriter agent.

Usage:
    python qa_checker.py check --file post.md [--keywords kw1,kw2] [--brief brief.md]
    python qa_checker.py wordcount --file post.md
    python qa_checker.py headings --file post.md
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

# Severity weights for scoring
SEVERITY_POINTS = {"high": 15, "medium": 5, "low": 2}

# AI-tell phrases (Spanish) — common in AI-generated content
AI_TELL_PHRASES = [
    "en el panorama actual",
    "cabe destacar que",
    "es importante señalar",
    "en este sentido",
    "resulta fundamental",
    "a lo largo de este artículo",
    "en la actualidad",
    "sin lugar a dudas",
    "es menester",
    "en definitiva",
    "hoy en día",
    "dicho lo anterior",
    "tal y como hemos mencionado",
    "a continuación exploraremos",
    "en este contexto",
    "no podemos olvidar que",
    "como hemos visto",
    "en primer lugar.*en segundo lugar",
    "en resumen",
    "a modo de conclusión",
    "es preciso destacar",
    "cobra especial relevancia",
    "juega un papel fundamental",
    "a la hora de",
    "en lo que respecta a",
]

# Bad anchor text patterns (Spanish)
BAD_ANCHORS = [
    "aquí",
    "haz clic",
    "haz click",
    "pulsa aquí",
    "pincha aquí",
    "click here",
    "este enlace",
    "este link",
    "más",
    "leer más",
    "ver más",
]


# --- Parsing ---

def parse_markdown(text: str) -> dict:
    """Parse Markdown text into structured components."""
    lines = text.split("\n")
    headings = []
    paragraphs = []
    lists = []
    links = []
    current_paragraph = []

    for line in lines:
        stripped = line.strip()

        # Headings
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading_match:
            if current_paragraph:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []
            level = len(heading_match.group(1))
            text_content = heading_match.group(2).strip()
            headings.append({"level": level, "text": text_content})
            continue

        # List items
        if re.match(r"^[-*+]\s+", stripped) or re.match(r"^\d+\.\s+", stripped):
            if current_paragraph:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []
            lists.append(stripped)
            continue

        # Links
        for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", stripped):
            links.append({"anchor": match.group(1), "url": match.group(2)})

        # Paragraph text
        if stripped:
            current_paragraph.append(stripped)
        elif current_paragraph:
            paragraphs.append(" ".join(current_paragraph))
            current_paragraph = []

    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))

    # Clean text for word counting (strip markdown syntax)
    clean_text = _strip_markdown(text)
    words = clean_text.split()

    return {
        "headings": headings,
        "paragraphs": paragraphs,
        "lists": lists,
        "links": links,
        "words": words,
        "word_count": len(words),
        "raw_text": text,
        "clean_text": clean_text,
    }


def _strip_markdown(text: str) -> str:
    """Remove Markdown syntax to get plain text for analysis."""
    # Remove images
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    # Remove links, keep anchor
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Remove headings markers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", text)
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Remove horizontal rules
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    # Remove list markers
    text = re.sub(r"^[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


# --- Checks ---

def check_word_count(parsed: dict) -> list[dict]:
    """Check total word count and per-section counts."""
    issues = []
    total = parsed["word_count"]

    if total < 300:
        issues.append({
            "check": "word_count",
            "severity": "high",
            "message": f"Total word count is {total} (minimum recommended: 300)",
        })
    elif total < 500:
        issues.append({
            "check": "word_count",
            "severity": "medium",
            "message": f"Total word count is {total} (consider expanding for better coverage)",
        })

    # Per-section word count (between H2s)
    sections = _split_by_h2(parsed["raw_text"])
    for section_title, section_text in sections:
        clean = _strip_markdown(section_text)
        section_words = len(clean.split())
        if section_words < 50 and section_title:
            issues.append({
                "check": "word_count",
                "severity": "low",
                "message": f"Section '{section_title}' has only {section_words} words",
            })

    return issues


def _split_by_h2(text: str) -> list[tuple[str, str]]:
    """Split text into (title, content) tuples by H2 headings."""
    sections = []
    current_title = ""
    current_lines = []

    for line in text.split("\n"):
        match = re.match(r"^##\s+(.+)$", line.strip())
        if match:
            if current_lines:
                sections.append((current_title, "\n".join(current_lines)))
            current_title = match.group(1)
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_title, "\n".join(current_lines)))

    return sections


def check_headings(parsed: dict) -> list[dict]:
    """Validate heading hierarchy."""
    issues = []
    headings = parsed["headings"]

    if not headings:
        issues.append({
            "check": "headings",
            "severity": "high",
            "message": "No headings found in content",
        })
        return issues

    h1_count = sum(1 for h in headings if h["level"] == 1)
    if h1_count == 0:
        issues.append({
            "check": "headings",
            "severity": "medium",
            "message": "No H1 found (WordPress title serves as H1, so this may be intentional)",
        })
    elif h1_count > 1:
        issues.append({
            "check": "headings",
            "severity": "high",
            "message": f"Multiple H1 headings found ({h1_count}). Only one H1 per page.",
        })

    # Check hierarchy: no level skips
    prev_level = 0
    for h in headings:
        if prev_level > 0 and h["level"] > prev_level + 1:
            issues.append({
                "check": "headings",
                "severity": "high",
                "message": f"Heading hierarchy skip: H{prev_level} → H{h['level']} at '{h['text'][:50]}'",
            })
        prev_level = h["level"]

    return issues


def check_keyword_density(parsed: dict, keywords: list[str]) -> list[dict]:
    """Check keyword density is between 0.5% and 2.5%."""
    issues = []
    if not keywords:
        return issues

    clean_lower = parsed["clean_text"].lower()
    total_words = parsed["word_count"]
    if total_words == 0:
        return issues

    for kw in keywords:
        kw_lower = kw.lower().strip()
        if not kw_lower:
            continue
        # Count occurrences (whole words/phrases, word boundaries)
        count = len(re.findall(r'\b' + re.escape(kw_lower) + r'\b', clean_lower))
        kw_word_count = len(kw_lower.split())
        density = (count * kw_word_count / total_words) * 100 if total_words > 0 else 0

        if density < 0.5:
            issues.append({
                "check": "keyword_density",
                "severity": "medium",
                "message": f"Keyword '{kw}' density is {density:.1f}% ({count} occurrences). Minimum: 0.5%",
            })
        elif density > 2.5:
            issues.append({
                "check": "keyword_density",
                "severity": "medium",
                "message": f"Keyword '{kw}' density is {density:.1f}% ({count} occurrences). Maximum: 2.5%",
            })

    return issues


def check_list_ratio(parsed: dict) -> list[dict]:
    """Check that list items don't dominate the content (anti list abuse)."""
    issues = []
    list_count = len(parsed["lists"])
    para_count = len(parsed["paragraphs"])

    if para_count == 0:
        return issues

    ratio = list_count / para_count
    if ratio > 0.4:
        issues.append({
            "check": "list_ratio",
            "severity": "medium",
            "message": f"List-to-paragraph ratio is {ratio:.2f} ({list_count} lists / {para_count} paragraphs). Max: 0.40",
        })

    return issues


def check_repetition(parsed: dict) -> list[dict]:
    """Check for repeated n-grams and repeated sentence starters."""
    issues = []
    words = [w.lower() for w in parsed["words"]]

    # 3-gram repetition (threshold: 3+ occurrences)
    if len(words) >= 3:
        trigrams = [" ".join(words[i : i + 3]) for i in range(len(words) - 2)]
        counts = Counter(trigrams)
        repeated = {gram: count for gram, count in counts.items() if count >= 3}
        # Filter out very common trigrams
        common_trigrams = {"de la", "en el", "que se", "de los", "de las", "en la", "que el", "que la"}
        for gram, count in sorted(repeated.items(), key=lambda x: -x[1])[:5]:
            first_two = " ".join(gram.split()[:2])
            if first_two not in common_trigrams:
                issues.append({
                    "check": "repetition",
                    "severity": "medium",
                    "message": f"Repeated 3-gram: '{gram}' ({count} times)",
                })

    # Sentence starter repetition
    sentences = re.split(r"[.!?]\s+", parsed["clean_text"])
    starters = []
    for s in sentences:
        s = s.strip()
        if s:
            first_words = " ".join(s.split()[:3]).lower()
            starters.append(first_words)

    starter_counts = Counter(starters)
    for starter, count in starter_counts.items():
        if count >= 3:
            issues.append({
                "check": "repetition",
                "severity": "medium",
                "message": f"Repeated sentence starter: '{starter}...' ({count} times)",
            })

    return issues


def check_ai_tell_phrases(parsed: dict) -> list[dict]:
    """Check for common AI-generated content markers."""
    issues = []
    text_lower = parsed["clean_text"].lower()

    for phrase in AI_TELL_PHRASES:
        matches = re.findall(phrase, text_lower)
        if matches:
            issues.append({
                "check": "ai_tell",
                "severity": "high",
                "message": f"AI-tell phrase detected: '{phrase}' ({len(matches)} occurrence{'s' if len(matches) > 1 else ''})",
            })

    return issues


def check_readability(parsed: dict) -> list[dict]:
    """Check average words per sentence (target: ≤ 25)."""
    issues = []
    sentences = re.split(r"[.!?]+\s+", parsed["clean_text"])
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return issues

    lengths = [len(s.split()) for s in sentences]
    avg = sum(lengths) / len(lengths)

    if avg > 25:
        issues.append({
            "check": "readability",
            "severity": "low",
            "message": f"Average sentence length is {avg:.1f} words (target: ≤ 25)",
        })

    # Flag individual very long sentences
    long_sentences = [(s, l) for s, l in zip(sentences, lengths) if l > 40]
    for sentence, length in long_sentences[:3]:
        preview = sentence[:80] + "..." if len(sentence) > 80 else sentence
        issues.append({
            "check": "readability",
            "severity": "low",
            "message": f"Long sentence ({length} words): '{preview}'",
        })

    return issues


def check_links(parsed: dict) -> list[dict]:
    """Check for non-descriptive anchor text."""
    issues = []

    for link in parsed["links"]:
        anchor_lower = link["anchor"].lower().strip()
        if anchor_lower in BAD_ANCHORS:
            issues.append({
                "check": "links",
                "severity": "medium",
                "message": f"Non-descriptive anchor text: '{link['anchor']}' → {link['url']}",
            })

    return issues


def check_meta_fields(parsed: dict, meta: dict | None = None) -> list[dict]:
    """Check SEO meta field lengths if provided in frontmatter or brief."""
    issues = []
    if not meta:
        return issues

    title = meta.get("seo_title", "")
    desc = meta.get("seo_description", "")

    if title and len(title) > 60:
        issues.append({
            "check": "meta_fields",
            "severity": "medium",
            "message": f"SEO title is {len(title)} chars (max 60): '{title[:65]}...'",
        })

    if desc and len(desc) > 155:
        issues.append({
            "check": "meta_fields",
            "severity": "medium",
            "message": f"Meta description is {len(desc)} chars (max 155): '{desc[:160]}...'",
        })

    return issues


# --- Scoring ---

def compute_score(issues: list[dict]) -> dict:
    """Compute quality score from issues. 100 base, deductions by severity."""
    score = 100
    deductions = {"high": 0, "medium": 0, "low": 0}

    for issue in issues:
        severity = issue.get("severity", "low")
        points = SEVERITY_POINTS.get(severity, 2)
        score -= points
        deductions[severity] += 1

    score = max(0, score)

    if score >= 90:
        rating = "excellent"
    elif score >= 75:
        rating = "good"
    elif score >= 50:
        rating = "needs_improvement"
    else:
        rating = "needs_revision"

    return {
        "score": score,
        "rating": rating,
        "deductions": deductions,
    }


# --- Frontmatter parsing ---

def extract_frontmatter_meta(text: str) -> tuple[str, dict]:
    """Extract YAML frontmatter meta fields if present. Returns (content, meta)."""
    meta = {}
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if match:
        frontmatter = match.group(1)
        content = text[match.end():]
        for line in frontmatter.split("\n"):
            kv = line.split(":", 1)
            if len(kv) == 2:
                key = kv[0].strip().lower().replace("-", "_").replace(" ", "_")
                val = kv[1].strip().strip('"').strip("'")
                meta[key] = val
        return content, meta
    return text, meta


# --- Subcommands ---

def cmd_check(args):
    """Run all QA checks on a Markdown file."""
    file_path = Path(args.file)
    if not file_path.exists():
        _error_exit(f"File not found: {file_path}")

    raw_text = file_path.read_text(encoding="utf-8")
    content, meta = extract_frontmatter_meta(raw_text)
    parsed = parse_markdown(content)

    keywords = []
    if args.keywords:
        keywords = [kw.strip() for kw in args.keywords.split(",") if kw.strip()]

    # Run all checks
    issues = []
    issues.extend(check_word_count(parsed))
    issues.extend(check_headings(parsed))
    issues.extend(check_keyword_density(parsed, keywords))
    issues.extend(check_list_ratio(parsed))
    issues.extend(check_repetition(parsed))
    issues.extend(check_ai_tell_phrases(parsed))
    issues.extend(check_readability(parsed))
    issues.extend(check_links(parsed))
    issues.extend(check_meta_fields(parsed, meta))

    scoring = compute_score(issues)

    result = {
        "file": str(file_path),
        "word_count": parsed["word_count"],
        "heading_count": len(parsed["headings"]),
        "score": scoring["score"],
        "rating": scoring["rating"],
        "deductions": scoring["deductions"],
        "issues": issues,
    }

    if keywords:
        result["keywords_checked"] = keywords

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_wordcount(args):
    """Show word count breakdown."""
    file_path = Path(args.file)
    if not file_path.exists():
        _error_exit(f"File not found: {file_path}")

    raw_text = file_path.read_text(encoding="utf-8")
    content, _ = extract_frontmatter_meta(raw_text)
    parsed = parse_markdown(content)

    sections = _split_by_h2(content)
    section_counts = []
    for title, text in sections:
        clean = _strip_markdown(text)
        count = len(clean.split())
        section_counts.append({"section": title or "(intro)", "words": count})

    result = {
        "file": str(file_path),
        "total_words": parsed["word_count"],
        "sections": section_counts,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_headings(args):
    """Show heading structure validation."""
    file_path = Path(args.file)
    if not file_path.exists():
        _error_exit(f"File not found: {file_path}")

    raw_text = file_path.read_text(encoding="utf-8")
    content, _ = extract_frontmatter_meta(raw_text)
    parsed = parse_markdown(content)

    outline = []
    for h in parsed["headings"]:
        indent = "  " * (h["level"] - 1)
        outline.append(f"{indent}H{h['level']}: {h['text']}")

    issues = check_headings(parsed)

    result = {
        "file": str(file_path),
        "heading_count": len(parsed["headings"]),
        "outline": outline,
        "issues": issues,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


# --- Helpers ---

def _error_exit(message: str, code: int = 1):
    print(json.dumps({"error": message}, ensure_ascii=False), file=sys.stderr)
    sys.exit(code)


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(
        description="Content QA checker for af_seo"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # check
    p_check = subparsers.add_parser("check", help="Run all QA checks on a Markdown file")
    p_check.add_argument("--file", required=True, help="Path to Markdown file")
    p_check.add_argument("--keywords", help="Comma-separated keywords to check density")
    p_check.add_argument("--brief", help="Path to SEO brief (for meta field validation)")
    p_check.set_defaults(func=cmd_check)

    # wordcount
    p_wc = subparsers.add_parser("wordcount", help="Show word count breakdown")
    p_wc.add_argument("--file", required=True, help="Path to Markdown file")
    p_wc.set_defaults(func=cmd_wordcount)

    # headings
    p_hd = subparsers.add_parser("headings", help="Show heading structure validation")
    p_hd.add_argument("--file", required=True, help="Path to Markdown file")
    p_hd.set_defaults(func=cmd_headings)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
