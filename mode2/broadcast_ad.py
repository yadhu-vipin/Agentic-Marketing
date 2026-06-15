"""
mode2/broadcast_ad.py
──────────────────────
MODE 2 — Broadcast Ad Campaign

Flow:
  Company submits their info
      → Generate ad copy (caption, hashtags, CTA)
      → Generate ad image via Pollinations (mode2/image_generator.py)
      → Post to Instagram Business via Facebook Graph API
      → Save campaign details to results/campaign_mode2.json

No scraping in Mode 2 — this is purely about creating
and publishing content to social media.

REQUIREMENTS:
  - Facebook Developer App
  - Instagram Business Account connected to a Facebook Page
  - Access Token with permissions:
      instagram_basic, instagram_content_publish,
      pages_read_engagement, pages_show_list
"""

import json
import os
import requests
from datetime import datetime

import config
from mode2.image_generator import generate_campaign_image


# ── Company Input ─────────────────────────────────────────────────────────────
# What the client submits for a broadcast campaign

COMPANY_INPUT = {
    "company_name":     "Artisan Loaf Bakery",
    "product":          "Sourdough Bread",
    "tagline":          "Baked fresh every morning in Indiranagar",
    "location":         "Bangalore, India",
    "target_audience":  "cafes, food lovers, health conscious buyers",
    "tone":             "warm and artisan",   # warm | professional | fun | urgent

    "contact":          "+91 98765 43210",
    "website":          "https://artisanloaf.in",

    # Instagram credentials
    # Get these from: https://developers.facebook.com
    "instagram_business_account_id": "YOUR_IG_BUSINESS_ACCOUNT_ID",
    "facebook_page_access_token":    "YOUR_PAGE_ACCESS_TOKEN",

    # Optional fallback if Pollinations generation fails
    "image_url": None,
}


# ── Ad Copy Generator (fully hardcoded, no AI) ────────────────────────────────

def generate_ad_copy(company_input: dict) -> dict:
    """
    Rule-based ad copy generation based on tone and product.
    Returns caption, hashtags, and an image prompt string.
    """
    company  = company_input["company_name"]
    product  = company_input["product"]
    tagline  = company_input["tagline"]
    location = company_input["location"]
    contact  = company_input["contact"]
    website  = company_input["website"]
    tone     = company_input["tone"]
    audience = company_input["target_audience"]

    # ── Caption based on tone ──────────────────────────────────────────────────
    captions = {
        "warm and artisan": f"""🍞 There's nothing quite like the smell of fresh {product} in the morning.

At {company}, we bake every loaf by hand — {tagline.lower()}.

Whether you're a cafe owner looking for a reliable supplier, or simply someone who loves real bread, we've got you covered.

📍 {location}
📞 {contact}
🌐 {website}

Bulk orders welcome. DM us or call to arrange a free sample drop.""",

        "professional": f"""{company} — Premium {product} supplier in {location}.

We supply fresh, handcrafted {product} daily to restaurants, cafes, and hotels across the city.

✔ Daily fresh delivery
✔ Bulk pricing available
✔ Free sample for first-time buyers

Contact us: {contact}
{website}""",

        "fun": f"""Hot take: your cafe deserves better bread. 🔥🍞

We're {company} and we make {product} that'll make your customers come back every single morning.

{tagline}. We're literally around the corner.

📞 {contact} — let's talk bread.""",

        "urgent": f"""⚡ LIMITED OFFER — Free sample delivery this week only!

{company} is now supplying fresh {product} to businesses in {location}.

First 10 cafes/restaurants to contact us get a FREE trial batch.

📞 {contact}
🌐 {website}

Don't miss out — DM us NOW.""",
    }

    caption = captions.get(tone, captions["warm and artisan"])

    # ── Hashtags based on product + audience ──────────────────────────────────
    base_tags = [
        f"#{product.replace(' ', '').lower()}",
        f"#{company.replace(' ', '').lower()}",
        "#freshlybaked",
        "#artisanbread",
        "#bangalorefood",
        "#bangalorecafe",
        "#foodbangalore",
        "#bulkorder",
        "#breadlover",
        "#homemade",
        "#supportlocal",
        "#bangalorerestaurant",
    ]

    audience_tags = []
    if "cafe" in audience:
        audience_tags += ["#cafebangalore", "#cafesupplier"]
    if "health" in audience:
        audience_tags += ["#healthyfood", "#cleaneating", "#wholewheat"]
    if "food lover" in audience:
        audience_tags += ["#foodie", "#instafood", "#foodphotography"]

    all_tags = list(dict.fromkeys(base_tags + audience_tags))  # dedup, preserve order
    hashtag_block = " ".join(all_tags[:20])  # Instagram allows up to 30

    # ── Image prompt (for manual use or DALL-E later) ─────────────────────────
    image_prompt = (
        f"A warm, artisan-style close-up photo of freshly baked {product} "
        f"on a rustic wooden surface, natural morning light, golden crust visible, "
        f"steam rising slightly, bakery setting in background, "
        f"warm tones, professional food photography."
    )

    return {
        "caption":      caption,
        "hashtags":     hashtag_block,
        "full_post":    f"{caption}\n\n{hashtag_block}",
        "image_prompt": image_prompt,
    }


# ── Instagram Publisher ───────────────────────────────────────────────────────

class InstagramPublisher:
    """
    Publishes to Instagram Business via Facebook Graph API.

    Two-step process (required by Meta):
      Step 1 → Create a media container (upload image + caption)
      Step 2 → Publish the container (makes it go live)
    """

    BASE_URL = "https://graph.facebook.com/v18.0"

    def __init__(self, ig_account_id: str, access_token: str):
        self.ig_account_id = ig_account_id
        self.access_token  = access_token

    def _post(self, endpoint: str, data: dict) -> dict:
        url      = f"{self.BASE_URL}/{endpoint}"
        data["access_token"] = self.access_token
        response = requests.post(url, data=data)
        return response.json()

    def create_media_container(self, image_url: str, caption: str) -> str | None:
        """
        Step 1: Upload the image and caption.
        Returns a container_id if successful.
        """
        print("\n  [Step 1] Creating media container...")

        result = self._post(
            f"{self.ig_account_id}/media",
            {
                "image_url": image_url,
                "caption":   caption,
            }
        )

        if "id" in result:
            print(f"  ✓ Container created: {result['id']}")
            return result["id"]
        else:
            print(f"  ✗ Failed to create container: {result}")
            return None

    def publish_container(self, container_id: str) -> dict:
        """
        Step 2: Publish the container — this is when it goes live.
        """
        print("\n  [Step 2] Publishing to Instagram...")

        result = self._post(
            f"{self.ig_account_id}/media_publish",
            {"creation_id": container_id}
        )

        if "id" in result:
            print(f"  ✓ Published! Post ID: {result['id']}")
        else:
            print(f"  ✗ Publish failed: {result}")

        return result

    def post(self, image_url: str, caption: str) -> dict:
        """
        Full two-step publish flow.
        Returns the final result dict.
        """
        container_id = self.create_media_container(image_url, caption)

        if not container_id:
            return {"error": "Container creation failed"}

        return self.publish_container(container_id)


# ── Save Campaign ─────────────────────────────────────────────────────────────

def save_campaign(campaign: dict, filename: str | None = None):
    filename = filename or config.CAMPAIGN_OUTPUT_FILE
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    with open(filename, "w") as f:
        json.dump(campaign, f, indent=2)
    print(f"\n✓ Campaign saved → {filename}")


# ── Main Mode 2 Runner ────────────────────────────────────────────────────────

def run_mode2():
    print("\n" + "="*50)
    print("  MODE 2 — Broadcast Ad Campaign")
    print("="*50)

    # Step 1 — Generate ad copy
    print("\n  Generating ad copy...")
    ad = generate_ad_copy(COMPANY_INPUT)

    print("\n  ── Generated Caption ──────────────────────")
    print(ad["caption"])
    print("\n  ── Hashtags ───────────────────────────────")
    print(ad["hashtags"])
    print("\n  ── Image Prompt ───────────────────────────")
    print(ad["image_prompt"])

    # Step 2 — Generate ad image via Pollinations
    print("\n  Generating ad image via Pollinations...")
    image_result = None
    image_url = COMPANY_INPUT.get("image_url")

    try:
        image_result = generate_campaign_image(
            ad["image_prompt"],
            company_name=COMPANY_INPUT["company_name"],
        )
        image_url = image_result["image_url"]
        print(f"\n  ── Generated Image URL ────────────────────")
        print(f"  {image_url}")
        if image_result.get("local_path"):
            print(f"  Local copy: {image_result['local_path']}")
    except Exception as e:
        print(f"\n  ✗ Pollinations image generation failed: {e}")
        if image_url:
            print(f"  Falling back to configured image_url: {image_url}")
        else:
            print("  No fallback image_url configured.")

    # Step 3 — Publish to Instagram
    ig_id = COMPANY_INPUT["instagram_business_account_id"]
    token = COMPANY_INPUT["facebook_page_access_token"]

    if not image_url:
        print("\n  ⚠ No image available — skipping Instagram publish.")
        publish_result = {"status": "skipped — no image generated"}
    elif "YOUR_" in ig_id or "YOUR_" in token:
        print("\n  ⚠ Instagram credentials not set — skipping publish step.")
        print("    Fill in COMPANY_INPUT with real credentials to post live.")
        publish_result = {"status": "skipped — credentials not configured"}
    else:
        publisher = InstagramPublisher(ig_id, token)
        publish_result = publisher.post(image_url, ad["full_post"])

    # Step 4 — Save campaign record
    campaign = {
        "company":        COMPANY_INPUT["company_name"],
        "product":        COMPANY_INPUT["product"],
        "tone":           COMPANY_INPUT["tone"],
        "ad_copy":        ad,
        "image":          image_result,
        "image_url":      image_url,
        "publish_result": publish_result,
        "created_at":     datetime.utcnow().isoformat(),
    }

    save_campaign(campaign)
    return campaign


if __name__ == "__main__":
    run_mode2()