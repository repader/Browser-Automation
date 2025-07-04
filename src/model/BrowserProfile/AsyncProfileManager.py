import asyncio
from typing import List

from src.model.BrowserProfile.AsyncBrowserProfile import AsyncBrowserProfile
from src.utils import ProfileRepository


class AsyncProfileManager:
    @staticmethod
    async def run_profile(params: dict):
        profile = AsyncBrowserProfile(**params)
        await profile.execute_actions(
            actions=params.get("actions")
        )

    @classmethod
    async def run_concurrently(cls, profiles_params: List[dict],max_concurrent: int = 5):
        semaphore = asyncio.Semaphore(max_concurrent)

        async def limited_task(params):
            async with semaphore:
                await cls.run_profile(params)

        tasks = [limited_task(params) for params in profiles_params]
        await asyncio.gather(*tasks)
