"""JustDial scraper (Playwright)."""

import urllib.parse
from datetime import datetime, timezone

from marketing_agent.services.scraper.base import PlaywrightScraper, register_scraper


@register_scraper
class JustdialScraper(PlaywrightScraper):
    name = "justdial"
    label = "JustDial"

    async def scrape_target(self, page, target, location, max_results) -> list[dict]:
        rows: list[dict] = []
        city = (location.split(",")[-1] if location else "").strip() or "Bangalore"

        try:
            await page.goto("https://www.justdial.com", timeout=30000)
            await page.wait_for_timeout(3000)
            await self._dismiss(page)

            loc_input = page.locator("input#city-auto-sug").first
            await loc_input.wait_for(state="visible", timeout=10000)
            await loc_input.click()
            await loc_input.fill("")
            await loc_input.type(city, delay=80)
            await page.wait_for_timeout(1500)
            await loc_input.press("Enter")
            await page.wait_for_timeout(1500)

            search_input = page.locator("input#main-auto").first
            await search_input.wait_for(state="visible", timeout=10000)
            await search_input.fill(target)
            await page.wait_for_timeout(800)
            await search_input.press("Enter")
            await page.wait_for_timeout(5000)
            await self._dismiss(page)
        except Exception:
            # Direct URL fallback
            try:
                url = (
                    f"https://www.justdial.com/"
                    f"{urllib.parse.quote(city.replace(' ', '-'))}/"
                    f"{urllib.parse.quote(target.replace(' ', '-'))}"
                )
                await page.goto(url, timeout=30000)
                await page.wait_for_timeout(3000)
                await self._dismiss(page)
            except Exception as exc:
                print(f"[justdial] fallback failed: {exc}")
                return rows

        await self._scroll(page, max_results)
        cards = page.locator("div.resultbox")
        cap = min(await cards.count(), max_results)

        for i in range(cap):
            try:
                card = cards.nth(i)
                rows.append(
                    {
                        "name": self.clean_text(await self._text(card, ".resultbox_title_anchor")),
                        "rating": self.clean_text(await self._text(card, ".resultbox_totalrate")),
                        "address": self.clean_text(await self._text(card, ".locatcity")),
                        "phone": self.extract_phone(await self._text(card, ".callcontent")),
                        "business_type": target,
                        "source": "justdial",
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
            except Exception as exc:
                print(f"[justdial] card {i + 1} failed: {exc}")
        return rows

    async def _text(self, card, selector) -> str | None:
        try:
            el = card.locator(selector).first
            return await el.inner_text() if await el.count() else None
        except Exception:
            return None

    async def _dismiss(self, page):
        try:
            await page.keyboard.press("Escape")
            for sel in ("span.close", "div.close_btn", "button.close", "a.close"):
                btn = page.locator(sel).first
                if await btn.count() and await btn.is_visible():
                    await btn.click()
                    await page.wait_for_timeout(400)
        except Exception:
            pass

    async def _scroll(self, page, max_results):
        for _ in range(5):
            if await page.locator("div.resultbox").count() >= max_results:
                break
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(1200)
