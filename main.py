import asyncio
from src.model import AsyncProfileManager
from src.utils import init_db, ProfileRepository, generate_password
from better_proxy import Proxy


async def main():
    await init_db()
    profile_repository = ProfileRepository()
    target = input("Создать профили - 1\nЗапустить профили - 2\n")
    if target == "1":
        flag = True
        while flag:
            name = input("Введите имя профиля\n")

            profile = await profile_repository.create_profile(name)
            profile_id = profile.id


            proxies = [line.split() for line in open('./data/proxy.txt', 'r').readlines()]
            twitters = [line.split() for line in open('./data/twitter.txt', 'r').readlines()]
            discords = [line.split() for line in open('./data/discord.txt', 'r').readlines()]
            emails = [line.split() for line in open('./data/emails.txt', 'r').readlines()]

            await profile.update_fields(
                data={
                    "wallet": None,
                    "password": generate_password(),
                    "email": emails[profile_id-1][0],
                    "proxy": Proxy.from_str(proxies[profile_id-1][0]).as_playwright_proxy,
                    "twitter": twitters[profile_id-1][0],
                    "discord": discords[profile_id-1][0],
                }
            )
            if input("Добавить ещё профиль? y/n\n") == "n":
                flag = False

    elif target == "2":
        profiles_config = [
            {
                "profile_name": f"{name}",
                "actions": [
                    {"action": "ServiceAuth"}
                ]
            }
            for name in [profile.name for profile in await profile_repository.get_all_profiles()]
        ]
        print(profiles_config)
        await AsyncProfileManager.run_concurrently(profiles_config,max_concurrent=3)
    elif target == "test":
        profiles_config = [
            {
                "profile_name": f"Test",
                "actions": [
                    {"action": "ServiceAuth"}
                ]
            }
            # for id in range(10)
        ]
        await AsyncProfileManager.run_concurrently(profiles_config, max_concurrent=3)

if __name__ == "__main__":
    asyncio.run(main())
