import asyncio

import logging

import random
from pathlib import Path
from typing import Optional, List, Dict, Any

from playwright.async_api import BrowserContext, async_playwright


from src.model import RabbyAuth
from src.model.AuthService import AuthService
from src.utils import BrowserActionsController, ProfileRepository, Profile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
extension_path = "C:/Users/Repade/AppData/Local/Google/Chrome/User Data/Profile 14/Extensions/acmacodkjbdgmoleebolmdjonilkdbch/0.93.35_0"
extension_path_2 = "C:/Users/Repade/AppData/Local/Google/Chrome/User Data/Profile 14/Extensions/hlkenndednhfkekhgcdicdfddnkalmdm/1.13.0_0"

class AsyncBrowserProfile:
    def __init__(
            self,
            profile_name: str,
            profiles_dir: str = "./data/profiles",
            browser_type: str = "chromium",
            extensions: Optional[List[str]] = None,
            proxy: Optional[str] = None,
            headless: bool = False,
            timeout: int = 30000,
            actions: Optional[List[Dict[str, Any]]] = None,
    ):
        self.profile_name = profile_name
        self.profiles_dir = Path(profiles_dir)
        self.browser_type = browser_type.lower()
        self.extensions = extensions or [extension_path, extension_path_2]
        self.proxy = proxy
        self.headless = headless
        self.timeout = timeout
        self.actions = actions or []

        self.profile_path = self.profiles_dir / self.profile_name
        self.profile_path.mkdir(parents=True, exist_ok=True)
        self.meta_file = self.profile_path / "profile_meta.json"

        self.playwright = None
        self.browser = None
        self.context = None

        self.controller = None

        self._profile: Optional[Profile] = None
        self.meta = None
        self.repo = ProfileRepository()

    async def initialize(self):
        """Инициализация профиля"""
        self._profile = await self.repo.get_profile(self.profile_name)
        if self._profile is None:
            self._profile = await self.repo.create_profile(self.profile_name)

        self.proxy = self._profile["data"]["proxy"]

        self.meta = self._profile['profile_metadata']

    async def save(self):
        """Сохранение изменений"""
        if self._profile:
            await self.repo.session.commit()

    def __setitem__(self, key: str, value: Any):
        """Установка значения через profile['key'] = value"""
        if not self._profile:
            raise RuntimeError("Profile not initialized. Use async with or call initialize() first")
        self._profile[key] = value

    def __getitem__(self, key: str) -> Any:
        """Получение значения через profile['key']"""
        if not self._profile:
            raise RuntimeError("Profile not initialized. Use async with or call initialize() first")
        return self._profile[key]

    async def update(self, **kwargs):
        """Массовое обновление метаданных"""
        if not self._profile:
            await self.initialize()

        for key, value in kwargs.items():
            self[key] = value

        await self.save()
    async def launch(self) -> BrowserContext:
        await self.initialize()
        """Запуск браузера с оптимизированными stealth-настройками"""
        self.playwright = await async_playwright().start()
        logger.debug("Инициализация Playwright завершена")

        # Базовые настройки запуска
        launch_options = {
            "user_data_dir": str(self.profile_path),
            "headless": self.headless,
            "viewport": {
                "width": self.meta["screen"]["width"],
                "height": self.meta["screen"]["height"],
            },
            "locale": self.meta["locale"],
            "timezone_id": self.meta["timezone"],
            "color_scheme": "light",
            "device_scale_factor": 1.0,
            "ignore_default_args": ["--enable-automation"]
        }

        # Аргументы командной строки
        args = [
            f"--user-agent={self.meta['user_agent']}",
            f"--lang={self.meta['locale']}",
            f"--timezone={self.meta['timezone']}",
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-first-run",
            "--disable-web-security",
            "--disable-notifications",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--remote-debugging-port=0",
            "--allow-chrome-scheme-url",
            "--disable-background-networking",
            "--disable-default-apps",
            "--disable-component-update",
            "--disable-sync",
            "--disable-features=OptimizationHints,TranslateUI",
            "--disable-component-extensions-with-background-pages",
            "--disable-logging",
            "--disable-software-rasterizer",

        ]

        # Добавляем расширения если они есть
        if self.extensions:
            args.extend([
                f"--disable-extensions-except={','.join(self.extensions)}",
                f"--load-extension={','.join(self.extensions)}"
            ])

        # Добавляем прокси если есть
        if self.proxy:
            launch_options["proxy"] = self.proxy

        # Убираем дубликаты аргументов
        seen_args = set()
        unique_args = []
        for arg in args:
            if arg.split('=')[0] not in seen_args:
                seen_args.add(arg.split('=')[0])
                unique_args.append(arg)

        launch_options["args"] = unique_args

        try:
            browser_launcher = getattr(self.playwright, self.browser_type)
            logger.debug(f"Запуск браузера с параметрами: {launch_options}")
            self.context = await browser_launcher.launch_persistent_context(**launch_options)
            logger.debug("Браузер успешно запущен")

            await self._apply_stealth_scripts()
            self.controller = BrowserActionsController(self.context)

            return self.context
        except Exception as e:
            logger.error(f"Ошибка запуска браузера: {str(e)}")
            await self.close()
            raise

    async def _apply_stealth_scripts(self):
        """Применяем ключевые stealth-техники"""
        await self.context.add_init_script(f"""
            // Удаление WebDriver-флагов
            delete Object.getPrototypeOf(navigator).webdriver;
            Object.defineProperty(navigator, 'webdriver', {{ get: () => false }});

            // Фиксим платформу
            Object.defineProperty(navigator, 'platform', {{
                get: () => '{self.meta["platform"]}'
            }});

            // Фиксим аппаратные характеристики
            Object.defineProperty(navigator, 'hardwareConcurrency', {{
                get: () => {random.choice([2, 4, 8])}
            }});

            // Подмена плагинов
            Object.defineProperty(navigator, 'plugins', {{
                get: () => [{{
                    name: 'Chrome PDF Plugin',
                    filename: 'internal-pdf-viewer',
                    description: 'Portable Document Format'
                }}]
            }});
        """)
        """Добавляет все необходимые stealth-переопределения включая WebGL/Canvas"""
        await self.context.add_init_script(f"""
                // Базовые stealth-правки
                delete Object.getPrototypeOf(navigator).webdriver;
                Object.defineProperty(navigator, 'webdriver', {{ get: () => false }});
                Object.defineProperty(navigator, 'platform', {{ get: () => '{self.meta["platform"]}' }});
                Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => 4 }});

                // Подмена Canvas (критично для fingerprinting)
                const canvasProto = HTMLCanvasElement.prototype;
                const originalGetContext = canvasProto.getContext;

                canvasProto.getContext = function(type) {{
                    if (type === '2d') {{
                        const ctx = originalGetContext.apply(this, arguments);

                        // Подмена методов Canvas
                        const originalFillText = ctx.fillText;
                        ctx.fillText = function(...args) {{
                            args[0] = args[0].replace(/automation/gi, '');
                            return originalFillText.apply(this, args);
                        }};

                        return ctx;
                    }}
                    return originalGetContext.apply(this, arguments);
                }};

                // Подмена WebGL (важно для сложных систем)
                const getParameterProxy = new Proxy(WebGLRenderingContext.prototype.getParameter, {{
                    apply(target, thisArg, args) {{
                        // Маскировка под стандартные значения
                        const param = args[0];
                        if (param === 37445) {{ // UNMASKED_VENDOR_WEBGL
                            return 'Google Inc. (NVIDIA)';
                        }}
                        if (param === 37446) {{ // UNMASKED_RENDERER_WEBGL
                            return 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)';
                        }}
                        return target.apply(thisArg, args);
                    }}
                }});

                WebGLRenderingContext.prototype.getParameter = getParameterProxy;

                // Дополнительно: шум для fingerprinting-атак
                Math.random = new Proxy(Math.random, {{
                    apply(target, thisArg, args) {{
                        const base = target.apply(thisArg, args);
                        return base + (Math.random() * 0.0001 - 0.00005); // Микро-вариации
                    }}
                }});
            """)
    async def close(self):
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()

    async def execute_actions(self, actions: Optional[List[Dict[str, Any]]] = None):
        try:
            await self.launch()
            actions_to_execute = actions if actions is not None else self.actions
            logger.info(f"Launching {self.profile_name}")

            if actions_to_execute:
                for action in actions_to_execute:
                    try:

                        if action["action"] == "ServiceAuth":
                            print(f"RabbyAuth action")
                            data = self._profile.data
                            seed_phrase = await RabbyAuth(self.context, self.controller, data["password"]).authenticate()
                            if seed_phrase is not None:
                                await self._profile.update_fields(
                                    data={
                                        "wallet": seed_phrase,
                                        "password": data["password"],
                                        "email": data["email"],
                                        "proxy": data["proxy"],
                                        "twitter": data["twitter"],
                                        "discord": data["discord"],
                                    }
                                )
                            print("1")
                            print(await AuthService(self.context, self.controller).login_discord(data["discord"]))
                            print("2")
                            await asyncio.sleep(20)
                    except Exception as e:
                        logger.error(f"[{self.profile_name}] Action failed: {e}")
                        continue
            logger.info(f"Finished {self.profile_name}")
        except Exception as e:
            logger.error(f"[{self.profile_name}] Error: {e}")
            raise
        finally:
            await self.close()