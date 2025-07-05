import tracemalloc
from typing import List, Optional
from urllib.parse import urlparse
from playwright.async_api import BrowserContext, Page


tracemalloc.start()
class TabManager:
    def __init__(self, context: BrowserContext):
        self.context = context

    async def _handle_new_page(self, new_page: Page):
        """Обрабатывает открытие новой вкладки"""
        # Ждем пока страница загрузится (или появится URL)
        await new_page.wait_for_load_state("domcontentloaded")

        if new_page.url != "about:blank":
            print(f"Открыта новая вкладка: {new_page.url}")
            await self._close_other_tabs(new_page)

    async def _close_other_tabs(self, keep_page: Page):
        """Закрывает все вкладки кроме указанной"""
        pages = self.context.pages
        closed_count = 0

        for page in pages:
            if page != keep_page and not page.is_closed():
                await page.close()
                closed_count += 1

        print(f"Закрыто {closed_count} других вкладок")

    async def open_url(self, url: str) -> Page:
        """Открывает URL и закрывает все другие вкладки"""
        # Закрываем все существующие вкладки

        # Открываем новую вкладку
        new_page = await self.context.new_page()
        await new_page.goto(url)
        for page in self.context.pages:
            if not page.is_closed() and not page == new_page:
                await page.close()

        return new_page

    async def get_current_page(self) -> Optional[Page]:
        """Возвращает текущую активную страницу (если есть)"""
        pages = self.context.pages
        return pages[-1] if pages else None

    async def get_current_page_url(self):
        page = await self.get_current_page()
        return page.url if page else None