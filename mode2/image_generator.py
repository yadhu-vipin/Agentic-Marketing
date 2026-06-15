"""
mode2/image_generator.py
────────────────────────
Pollinations.ai image generation for Mode 2 broadcast campaigns.

Uses the free gen.pollinations.ai GET endpoint — no API key required.
Returns a publicly accessible URL suitable for Instagram's image_url parameter,
and optionally saves a local copy under results/campaign_images/.
"""

import os
import re
import time
import uuid
from urllib.parse import quote, urlencode

import requests

import config


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:40] or "campaign"


def build_image_url(
    prompt: str,
    *,
    model: str | None = None,
    width: int | None = None,
    height: int | None = None,
    seed: int | None = None,
) -> str:
    """Build a publicly accessible Pollinations image URL from a text prompt."""
    encoded = quote(prompt)
    params = {
        "model": model or config.POLLINATIONS_MODEL,
        "width": width or config.POLLINATIONS_WIDTH,
        "height": height or config.POLLINATIONS_HEIGHT,
    }
    if seed is not None:
        params["seed"] = seed
    if config.POLLINATIONS_API_KEY:
        params["key"] = config.POLLINATIONS_API_KEY

    return f"{config.POLLINATIONS_BASE_URL}/{encoded}?{urlencode(params)}"


def _fetch_image(url: str) -> bytes:
    last_error = None
    for attempt in range(1, config.POLLINATIONS_MAX_RETRIES + 1):
        try:
            print(f"  [Pollinations] Requesting image (attempt {attempt}/{config.POLLINATIONS_MAX_RETRIES})...")
            response = requests.get(url, timeout=config.POLLINATIONS_TIMEOUT_SEC)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                raise ValueError(f"Unexpected content type: {content_type}")

            if len(response.content) < 1000:
                raise ValueError("Response too small to be a valid image")

            return response.content

        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            if attempt < config.POLLINATIONS_MAX_RETRIES:
                print(f"  [Pollinations] Attempt {attempt} failed: {exc}. Retrying in 5s...")
                time.sleep(5)

    raise RuntimeError(f"Pollinations image generation failed after {config.POLLINATIONS_MAX_RETRIES} attempts: {last_error}")


def generate_campaign_image(
    prompt: str,
    *,
    company_name: str = "campaign",
    model: str | None = None,
    width: int | None = None,
    height: int | None = None,
    save_local: bool = True,
) -> dict:
    """
    Generate an ad image via Pollinations.

    Returns:
        image_url   — public URL (use for Instagram image_url)
        local_path  — saved file path, or None
        prompt      — original prompt
        model       — model used
        width/height — dimensions
        seed        — random seed used
    """
    seed = uuid.uuid4().int % (2**31)
    image_url = build_image_url(prompt, model=model, width=width, height=height, seed=seed)

    image_bytes = _fetch_image(image_url)

    local_path = None
    if save_local:
        os.makedirs(config.CAMPAIGN_IMAGES_DIR, exist_ok=True)
        filename = f"{_slugify(company_name)}_{seed}.jpg"
        local_path = os.path.join(config.CAMPAIGN_IMAGES_DIR, filename)
        with open(local_path, "wb") as f:
            f.write(image_bytes)
        print(f"  [Pollinations] ✓ Image saved locally → {local_path}")

    print(f"  [Pollinations] ✓ Public image URL ready")
    return {
        "image_url": image_url,
        "local_path": local_path,
        "prompt": prompt,
        "model": model or config.POLLINATIONS_MODEL,
        "width": width or config.POLLINATIONS_WIDTH,
        "height": height or config.POLLINATIONS_HEIGHT,
        "seed": seed,
        "size_bytes": len(image_bytes),
    }
