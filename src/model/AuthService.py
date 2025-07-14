import asyncio

from typing import Optional

from playwright.async_api import BrowserContext

from src.utils import BrowserActionsController


class AuthService:
    def __init__(self, context: BrowserContext, controller: BrowserActionsController):
        self.context = context
        self.controller = controller

    async def login(self, token_twitter: Optional[str] = None, token_discord: Optional[str] = None) -> None:
        if token_twitter:
            await self.login_twitter(token_twitter)
        if token_discord:
            await self.login_discord(token_discord)
    async def login_twitter(self, token: str) -> bool:
        cookies = [{
            "name": "auth_token",
            "value": token,
            "domain": ".twitter.com",
            "path": "/",
            "secure": True,
            "httpOnly": True,
            "sameSite": "Lax"

        },{
            "name": "auth_token",
            "value": token,
            "domain": ".x.com",
            "path": "/",
            "secure": True,
            "httpOnly": True,
            "sameSite": "Lax"
        }]
        await self.context.add_cookies(cookies)
        await self.controller.navigate("https://twitter.com/")

        return True

    async def login_discord(self, token: str) -> None:
        await self.controller.navigate("https://discord.com/login")

        script = f"""
            const token = "{token}";
            setInterval(() => {{
                document.body.appendChild(document.createElement('iframe')).contentWindow.localStorage.token = `"${{token}}"`;
            }}, 50);
            setTimeout(() => {{
                location.reload();
            }}, 2500);
        """

        await self.context.add_init_script(script)
        await asyncio.sleep(100)

