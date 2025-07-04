from typing import List
from urllib.parse import urlparse

from playwright.async_api import BrowserContext, Page


class TabManager:
    def __init__(self, context: BrowserContext):
        self.context = context
        self.tab_urls = {}

    async def open_or_switch(self, url: str, switch_if_partial_match: bool = True) -> Page:
        target_domain = urlparse(url).netloc
        pages = self.context.pages

        for page in pages:
            current_url = page.url
            if (url == current_url) or (switch_if_partial_match and target_domain in current_url):
                print(f"Переключено на существующую вкладку: {current_url}")
                await page.bring_to_front()
                return page

        new_page = await self.context.new_page()
        await new_page.goto(url)
        print(f"Открыта новая вкладка: {url}")
        return new_page

    async def get_all_open_urls(self) -> List[str]:
        return [page.url for page in self.context.pages]

    async def close_duplicate_tabs(self):
        seen_urls = set()
        pages = self.context.pages

        for page in pages:
            current_url = page.url
            if current_url in seen_urls:
                await page.close()
            else:
                seen_urls.add(current_url)