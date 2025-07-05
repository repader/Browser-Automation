import asyncio
from asyncio import sleep
from typing import Optional

from playwright.async_api import BrowserContext, Page

from src.utils import TabManager
from src.utils.TabManager import TabManager
password = "N41e4EA2Zv"
class RabbyAuth:
    def __init__(self, context: BrowserContext, tab_manager: TabManager):
        self.context = context
        self.tab_manager = tab_manager
        self.page: Optional[Page] = None

    async def authenticate(self):

        self.page = await self.tab_manager.open_url("chrome-extension://acmacodkjbdgmoleebolmdjonilkdbch/index.html")
        await asyncio.sleep(5)
        if "chrome-extension://acmacodkjbdgmoleebolmdjonilkdbch/index.html#/unlock" == await self.tab_manager.get_current_page_url():
            return await self.login()
        else:
            return await self.register()

    async def register(self):
        print("register")
        await self.page.get_by_role("button", name="Next").click()
        await self.page.get_by_role("button", name="Get Started").click()
        await self.page.get_by_text("Create New Seed Phrase").click()
        await self.page.get_by_placeholder("Password must be at least 8 characters long").fill(password)
        await self.page.get_by_placeholder("Confirm password").fill(password)
        await self.page.get_by_role("button", name="Next").click()
        await asyncio.sleep(2)

        self.page = await self.tab_manager.open_url(
            "chrome-extension://acmacodkjbdgmoleebolmdjonilkdbch/index.html#/mnemonics/create")
        await self.page.reload()
        await self.page.get_by_role("button", name="Show Seed Phrase").click()
        await asyncio.sleep(2)
        seed_phrase = " ".join([await word.text_content() for word in await self.page.locator('.text').all()])


        await asyncio.sleep(2)
        await self.page.get_by_role("button", name="I've Saved the Phrase").click()
        await asyncio.sleep(2)
        await self.page.get_by_role("button", name="Get Started").click()
        await asyncio.sleep(2)

        return seed_phrase

    async def login(self):
        print("login")
        await self.page.get_by_placeholder("Enter the Password to Unlock").fill(password)
        await self.page.get_by_role("button", name="Unlock").click()

        return None

    async def test(self):
        self.page = await self.tab_manager.open_url(
            "chrome-extension://acmacodkjbdgmoleebolmdjonilkdbch/index.html")

        await asyncio.sleep(200)