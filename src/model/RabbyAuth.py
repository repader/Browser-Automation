import asyncio
from typing import Optional

from playwright.async_api import BrowserContext, Page

from src.utils import TabManager
from src.utils.TabManager import TabManager
password = "N41e4EA2Zv"
class RabbyAuth:
    def __init__(self, context: BrowserContext, tab_manager: TabManager):
        self.context = context
        self.tab_manager = tab_manager
        self.is_new_wallet = True
        self.page: Optional[Page] = None

    async def authenticate(self):
        await asyncio.sleep(10)
        for page in self.context.pages:
            if "chrome-extension://acmacodkjbdgmoleebolmdjonilkdbch" in page.url:
                await page.close()

        self.page = await self.tab_manager.open_or_switch("chrome-extension://acmacodkjbdgmoleebolmdjonilkdbch/index.html")
        await asyncio.sleep(2)
        for page in self.context.pages:
            if "chrome-extension://acmacodkjbdgmoleebolmdjonilkdbch/index.html#/unlock" in page.url:
                self.is_new_wallet = False

        if self.is_new_wallet:
            await self.register()
        else:
            await self.login()
    async def register(self):
        await self.page.get_by_role("button", name="Next").click()
        await self.page.get_by_role("button", name="Get Started").click()
        await self.page.get_by_text("Create New Seed Phrase").click()
        await self.page.get_by_placeholder("Password must be at least 8 characters long").fill(password)
        await self.page.get_by_placeholder("Confirm password").fill(password)
        await self.page.get_by_role("button", name="Next").click()
        await asyncio.sleep(2)

        print(await self.tab_manager.get_all_open_urls())
        await self.tab_manager.close_duplicate_tabs()

        self.page = await self.tab_manager.open_or_switch(
            "chrome-extension://acmacodkjbdgmoleebolmdjonilkdbch/index.html#/mnemonics/create")
        await self.page.reload()
        await self.page.get_by_role("button", name="Show Seed Phrase").click()
        await asyncio.sleep(2)
        seed_phrase = " ".join([await word.text_content() for word in await self.page.locator('.text').all()])
        await asyncio.sleep(2)
        await self.page.get_by_role("button", name="I've Saved the Phrase").click()
        await self.page.get_by_role("button", name="Get Started").click()
        await self.page.get_by_role("button", name="Done").click()

    async def login(self):
        await self.page.get_by_placeholder("Enter the Password to Unlock").fill(password)
        await self.page.get_by_role("button", name="Unlock").click()