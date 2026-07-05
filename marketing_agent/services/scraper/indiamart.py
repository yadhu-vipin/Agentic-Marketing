"""IndiaMART directory scraper (Playwright)."""

import re
import urllib.parse
from datetime import datetime, timezone

from marketing_agent.services.scraper.base import PlaywrightScraper, register_scraper


@register_scraper
class IndiaMartScraper(PlaywrightScraper):
    name = "indiamart"
    label = "IndiaMART"

    CARD_SELECTORS = ["div.pcard", "div.lst-cl", "div[class*='company-card']", "li.lst-cl"]

    async def scrape_target(self, page, target, location, max_results) -> list[dict]:
        rows: list[dict] = []
        query = f"{target} {location}".strip()
        url = f"https://dir.indiamart.com/search.mp?ss={urllib.parse.quote_plus(query)}"

        try:
            await page.goto(url, timeout=45000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            await self._dismiss(page)
            await self._scroll(page, max_results)
        except Exception as exc:
            print(f"[indiamart] navigation failed: {exc}")
            return rows

        cards = await self._cards(page)
        cap = min(len(cards), max_results)
        for i in range(cap):
            try:
                card = cards[i]
                name = self.clean_text(
                    await self._text(card, [".companyname", ".company-name", "h2", "h3"])
                )
                if not name:
                    continue
                text_blob = self.clean_text(await card.inner_text()) or ""
                member = re.search(r"member\s+since\s+(\d{4})", text_blob, re.I)
                rows.append(
                    {
                        "name": name,
                        "address": self.clean_text(
                            await self._text(card, [".cityname", ".city", ".loc"])
                        )
                        or location,
                        "category": self.clean_text(
                            await self._text(card, [".prd-cat", ".cat-name"])
                        )
                        or target,
                        "phone": self.extract_phone(text_blob),
                        "business_type": target,
                        "source": "indiamart",
                        "member_since": member.group(1) if member else None,
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
            except Exception as exc:
                print(f"[indiamart] card {i + 1} failed: {exc}")
        return rows

    async def _cards(self, page) -> list:
        for sel in self.CARD_SELECTORS:
            loc = page.locator(sel)
            if await loc.count():
                return [loc.nth(i) for i in range(await loc.count())]
        return []

    async def _text(self, card, selectors) -> str | None:
        for sel in selectors:
            try:
                el = card.locator(sel).first
                if await el.count():
                    txt = await el.inner_text()
                    if txt and len(txt) < 200:
                        return txt
            except Exception:
                continue
        return None

    async def _dismiss(self, page):
        try:
            await page.keyboard.press("Escape")
            for sel in ("button.close", ".modal-close", "#close"):
                btn = page.locator(sel).first
                if await btn.count() and await btn.is_visible():
                    await btn.click()
                    await page.wait_for_timeout(400)
        except Exception:
            pass

    async def _scroll(self, page, max_results):
        for _ in range(6):
            if len(await self._cards(page)) >= max_results:
                break
            await page.mouse.wheel(0, 2500)
            await page.wait_for_timeout(1200)
