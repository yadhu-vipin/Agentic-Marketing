import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:

        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://www.google.com")

        await page.fill(
            'textarea[name="q"]',
            "software engineers bangalore"
        )

        await page.keyboard.press("Enter")

        await page.wait_for_timeout(5000)

        print(await page.title())

        links = await page.locator("a[href]").evaluate_all(
            """
            els => els.map(e => ({
                text: (e.innerText || "").trim(),
                href: e.href
            }))
            """
        )

        count = 0

        for link in links:

            if count >= 10:
                break

            text = link["text"]
            href = link["href"]

            if not text:
                continue

            if not href.startswith("http"):
                continue

            if "google." in href:
                continue

            print("\nRESULT", count + 1)
            print("TITLE:", text)
            print("URL:", href)

            count += 1

        await browser.close()


asyncio.run(main())