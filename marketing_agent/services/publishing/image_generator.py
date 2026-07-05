"""
Generate an advertisement preview image from a text prompt using
Pollinations.ai (free, no API key).
"""

import uuid
from urllib.parse import quote, urlencode

from marketing_agent.configs.settings import get_settings


def build_image_url(prompt: str, *, seed: int | None = None) -> str:
    settings = get_settings()
    params = {
        "model": settings.pollinations_model,
        "width": settings.pollinations_width,
        "height": settings.pollinations_height,
        "nologo": "true",
    }
    if seed is not None:
        params["seed"] = seed
    return f"{settings.pollinations_base_url}/{quote(prompt)}?{urlencode(params)}"


def generate_ad_image(prompt: str, *, seed: int | None = None) -> dict:
    """Return a renderable image URL for the given prompt."""
    settings = get_settings()
    seed = seed if seed is not None else uuid.uuid4().int % (2**31)
    return {
        "image_url": build_image_url(prompt, seed=seed),
        "prompt": prompt,
        "seed": seed,
        "width": settings.pollinations_width,
        "height": settings.pollinations_height,
    }
