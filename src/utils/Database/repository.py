import random
from datetime import datetime
from typing import Dict, Any

from sqlalchemy import select

from src.utils.Database.models import Profile, async_session


class ProfileRepository:
    def _generate_user_agent(self) -> str:
        """Генерирует User-Agent строку"""
        platform = random.choice(["Win32", "MacIntel"])
        platform_map = {
            "Win32": "(Windows NT 10.0; Win64; x64)",
            "MacIntel": "(Macintosh; Intel Mac OS X 10_15_7)"
        }
        chrome_ver = f"{random.randint(100, 115)}.0.{random.randint(1000, 9999)}.{random.randint(10, 99)}"
        return f"Mozilla/5.0 {platform_map[platform]} AppleWebKit/537.36 Chrome/{chrome_ver} Safari/537.36"

    async def get_profile(self, name: str) -> Profile:
        async with async_session() as session:
            result = await session.execute(select(Profile).where(Profile.name == name))

            return result.scalar_one_or_none()

    async def create_profile(self, name: str) -> Profile:
        profile = Profile(name=name)
        profile.update_metadata(
            user_agent=self._generate_user_agent(),
            locale=random.choice(["en-US", "ru-RU", "fr-FR"]),
            timezone=random.choice(["Europe/Moscow", "America/New_York"]),
            screen={
                "width": random.randint(1200, 1920),
                "height": random.randint(800, 1080)
            },
            platform=random.choice(["Win32", "MacIntel"]),
            created_at=datetime.now().isoformat()
        )
        async with async_session() as session:
            session.add(profile)
            await session.commit()
        return profile