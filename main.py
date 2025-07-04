import asyncio
from src.model import AsyncProfileManager

async def main():
    profiles_config = [
        {
            "profile_name": "profile_async1",
            "actions": [
                {"action": "RabbyAuth"}
            ]
        },
        {
            "profile_name": "profile_async2",
            "actions": [
                {"action": "RabbyAuth"}
            ]
        },{
            "profile_name": "profile_async3",
            "actions": [
                {"action": "RabbyAuth"}
            ]
        },
    ]
    await AsyncProfileManager.run_concurrently(profiles_config, max_concurrent=3)

if __name__ == "__main__":
    target = input("Создать профили - 1\nЗапустить профили - 2\n")

    if target == "1":
        asyncio.run(main())
    elif target == "2":
        pass