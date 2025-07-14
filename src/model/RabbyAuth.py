import asyncio
from asyncio import sleep
from typing import Optional

from playwright.async_api import BrowserContext, Page

from src.utils import BrowserActionsController


class RabbyAuth:
    def __init__(self, context: BrowserContext, controller: BrowserActionsController, password: str):
        self.context = context
        self.controller = controller
        self.password = password
        self.page: Optional[Page] = None

    async def authenticate(self):

        self.page = await self.controller.navigate("chrome-extension://acmacodkjbdgmoleebolmdjonilkdbch/index.html")
        await asyncio.sleep(5)
        if "chrome-extension://acmacodkjbdgmoleebolmdjonilkdbch/index.html#/unlock" == await self.controller.get_current_page_url():
            return await self.login()
        else:
            return await self.register()

    async def register(self):
        print("register")
        await self.controller.click(self.page.get_by_role("button", name="Next"))
        await self.controller.click(self.page.get_by_role("button", name="Get Started"))
        await self.controller.click(self.page.get_by_text("Create New Seed Phrase"))
        await self.controller.typing(self.page.get_by_placeholder("Password must be at least 8 characters long"), self.password)
        await self.controller.typing(self.page.get_by_placeholder("Confirm password"), self.password)

        await self.controller.click(self.page.get_by_role("button", name="Next"))
        await asyncio.sleep(2)

        self.page = await self.controller.navigate("chrome-extension://acmacodkjbdgmoleebolmdjonilkdbch/index.html#/mnemonics/create")
        await self.page.reload()
        await self.controller.click(self.page.get_by_role("button", name="Show Seed Phrase"))

        await asyncio.sleep(2)
        seed_phrase = " ".join([await word.text_content() for word in await self.page.locator('.text').all()])

        await self.controller.click(self.page.get_by_role("button", name="I've Saved the Phrase"))
        await self.controller.click(self.page.get_by_role("button", name="Get Started"))
        return seed_phrase

    async def login(self):
        print("login")
        await self.controller.typing(self.page.get_by_placeholder("Enter the Password to Unlock"), self.password)

        await self.controller.click(self.page.get_by_role("button", name="Unlock"))
        return None