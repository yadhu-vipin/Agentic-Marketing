"""Google Maps scraper (Playwright)."""

import asyncio
import re
from datetime import datetime, timezone

from marketing_agent.services.scraper import website_enricher
from marketing_agent.services.scraper.base import PlaywrightScraper, register_scraper


@register_scraper
class GoogleMapsScraper(PlaywrightScraper):
    name = "google_maps"
    label = "Google Maps"

    async def scrape_target(self, page, target, location, max_results) -> list[dict]:
        query = f"{target} in {location}".strip()
        rows: list[dict] = []

        await page.goto("https://www.google.com/maps")
        try:
            consent = page.locator("form[action*='consent'] button").first
            if await consent.is_visible():
                await consent.click()
                await page.wait_for_timeout(2000)
        except Exception:
            pass

        await page.locator('input[name="q"]').fill(query)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(5000)

        results = page.locator('a[href*="/place/"]')
        cap = min(await results.count(), max_results)

        for i in range(cap):
            try:
                results = page.locator('a[href*="/place/"]')
                business = results.nth(i)
                quick_name = await business.get_attribute("aria-label")
                await business.click()
                await page.wait_for_timeout(3000)

                detail = await self._detail(page)
                if not detail.get("name") or detail["name"].lower() in (
                    "results",
                    "search results",
                ):
                    detail["name"] = self.clean_text(quick_name)
                detail["business_type"] = target
                rows.append(detail)

                await page.go_back()
                await page.wait_for_timeout(2500)
            except Exception as exc:
                print(f"[google_maps] item {i + 1} failed: {exc}")
        return await self._enrich_website_rows(rows)

    async def _enrich_website_rows(self, rows: list[dict]) -> list[dict]:
        """Visit Maps website links and merge contact/context signals into rows."""
        if not rows:
            return rows

        total = len([row for row in rows if row.get("website")])
        if not total:
            return rows

        self.emit(f"enriching {total} Google Maps website link(s)...")

        async def enrich_one(idx: int, row: dict) -> dict:
            if not row.get("website"):
                return row
            self.emit(f"  website {idx}/{total}: {row.get('website')}")
            enriched = await asyncio.to_thread(website_enricher.enrich_row, row)
            meta = dict(enriched.get("metadata") or {})
            meta["google_maps_website_enriched"] = bool(meta.get("website_enriched"))
            enriched["metadata"] = meta
            return enriched

        enriched: list[dict] = []
        website_idx = 0
        for row in rows:
            if row.get("website"):
                website_idx += 1
                enriched.append(await enrich_one(website_idx, row))
            else:
                enriched.append(row)
        return enriched

    async def _detail(self, page) -> dict:
        await page.wait_for_timeout(1500)
        detail: dict = {
            "source": "google_maps",
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

        async def grab(getter):
            try:
                return await getter()
            except Exception:
                return None

        detail["name"] = self.clean_text(
            await grab(lambda: page.get_by_role("heading", level=1).first.inner_text())
        )
        rating = await grab(
            lambda: page.get_by_role("img", name=re.compile(r"star", re.I))
            .first.get_attribute("aria-label")
        )
        detail["rating"] = self.clean_text(rating)
        addr = await grab(
            lambda: page.get_by_role("button", name=re.compile(r"address", re.I))
            .first.get_attribute("aria-label")
        )
        detail["address"] = self.clean_text(addr.split(":", 1)[-1]) if addr else None
        phone = await grab(
            lambda: page.get_by_role("button", name=re.compile(r"phone", re.I))
            .first.get_attribute("aria-label")
        )
        detail["phone"] = self.extract_phone(phone) if phone else None
        detail["open_status"] = self.clean_text(
            await grab(
                lambda: page.get_by_text(
                    re.compile(r"^(Open|Closed|Opens|Closes)", re.I)
                ).first.inner_text()
            )
        )
        detail["website"] = await grab(
            lambda: page.get_by_role("link", name=re.compile(r"website", re.I))
            .first.get_attribute("href")
        )
        return detail
