#!/usr/bin/env python3
"""Featured image generator for af_seo.

Generates images using Gemini 2.5 Flash Image (Nano Banana) via Google AI API key.
Used by wp-implementer agent. The image prompt is provided by the marketing-copywriter
agent in copy deliverables.

Usage:
    python image_generator.py generate --prompt "A visual metaphor..." [--output image.jpg]
    python image_generator.py generate --prompt "..." --aspect-ratio 16:9 --size 2K
    python image_generator.py optimize --file image.png [--output optimized.jpg]
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image as PILImage

# Load .env from workspace root
_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_WORKSPACE_ROOT / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
IMAGE_MODEL = "gemini-2.5-flash-image"
DEFAULT_OUTPUT = "outputs/featured_image.png"


def get_client():
    """Initialize Gemini client with API key."""
    if not GEMINI_API_KEY:
        _error_exit("GEMINI_API_KEY not set in .env")
    return genai.Client(api_key=GEMINI_API_KEY)


# --- Generate ---

def generate_image(prompt: str, output_path: str, aspect_ratio: str = "16:9", image_size: str = "2K") -> dict:
    """Generate an image from a text prompt using Gemini Nano Banana."""
    client = get_client()

    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=image_size,
        ),
    )

    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=prompt,
        config=config,
    )

    # Extract image from response parts
    image_saved = False
    alt_text = ""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    for part in response.parts:
        if part.inline_data is not None:
            image = part.as_image()
            image.save(str(output))
            image_saved = True
        elif part.text is not None:
            alt_text = part.text.strip()

    if not image_saved:
        _error_exit("No image was generated. The model returned only text. Try rephrasing the prompt.")

    # Optimize for WordPress
    optimized_path = optimize_for_wordpress(str(output))

    file_size = os.path.getsize(optimized_path)
    result = {
        "action": "generate",
        "file": optimized_path,
        "size_bytes": file_size,
        "aspect_ratio": aspect_ratio,
        "model": IMAGE_MODEL,
    }
    if alt_text:
        result["alt_text_suggestion"] = alt_text

    return result


# --- Optimize ---

def optimize_for_wordpress(image_path: str, max_width: int = 1920, quality: int = 85) -> str:
    """Optimize image for WordPress: resize + JPEG compression."""
    img = PILImage.open(image_path)

    # Resize if wider than max_width
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), PILImage.Resampling.LANCZOS)

    # Convert to RGB for JPEG (handles RGBA, palette modes)
    if img.mode in ("RGBA", "LA", "P"):
        background = PILImage.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        if img.mode in ("RGBA", "LA"):
            background.paste(img, mask=img.split()[-1])
        else:
            background.paste(img)
        img = background

    # Save as optimized JPEG
    out_path = str(Path(image_path).with_suffix(".jpg"))
    img.save(out_path, format="JPEG", quality=quality, optimize=True)

    # Remove original PNG if we created a new JPG
    if out_path != image_path and Path(image_path).exists():
        Path(image_path).unlink()

    return out_path


# --- Subcommands ---

def cmd_generate(args):
    """Generate a featured image from a text prompt."""
    output = args.output or DEFAULT_OUTPUT
    result = generate_image(
        prompt=args.prompt,
        output_path=output,
        aspect_ratio=args.aspect_ratio,
        image_size=args.size,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_optimize(args):
    """Optimize an existing image for WordPress."""
    file_path = Path(args.file)
    if not file_path.exists():
        _error_exit(f"File not found: {file_path}")

    output = args.output or str(file_path)
    # Copy to output first if different
    if output != str(file_path):
        import shutil
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(file_path), output)

    optimized = optimize_for_wordpress(output)
    file_size = os.path.getsize(optimized)
    print(json.dumps({
        "action": "optimize",
        "file": optimized,
        "size_bytes": file_size,
    }, ensure_ascii=False, indent=2))


# --- Helpers ---

def _error_exit(message: str, code: int = 1):
    print(json.dumps({"error": message}, ensure_ascii=False), file=sys.stderr)
    sys.exit(code)


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(
        description="Featured image generator using Gemini Nano Banana"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate
    p_gen = subparsers.add_parser("generate", help="Generate image from text prompt")
    p_gen.add_argument("--prompt", required=True, help="Text prompt describing the image")
    p_gen.add_argument("--output", "-o", help=f"Output file path (default: {DEFAULT_OUTPUT})")
    p_gen.add_argument("--aspect-ratio", default="16:9",
                       choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
                       help="Aspect ratio (default: 16:9)")
    p_gen.add_argument("--size", default="2K", choices=["1K", "2K", "4K"],
                       help="Image size (default: 2K)")
    p_gen.set_defaults(func=cmd_generate)

    # optimize
    p_opt = subparsers.add_parser("optimize", help="Optimize existing image for WordPress")
    p_opt.add_argument("--file", required=True, help="Path to image file")
    p_opt.add_argument("--output", "-o", help="Output path (default: overwrite original)")
    p_opt.set_defaults(func=cmd_optimize)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
