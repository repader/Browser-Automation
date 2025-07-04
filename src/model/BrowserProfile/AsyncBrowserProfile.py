import json
import logging
from datetime import datetime
import random
from pathlib import Path
from typing import Optional, List, Dict, Any

from playwright.async_api import BrowserContext, async_playwright


from src.model import RabbyAuth
from src.utils import TabManager
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
extension_path = "C:/Users/Repade/AppData/Local/Google/Chrome/User Data/Profile 14/Extensions/acmacodkjbdgmoleebolmdjonilkdbch/0.93.35_0"

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
        self.extensions = extensions or [extension_path]
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
        self.tab_manager = None

        self.meta = {}
        self._init_metadata()

    def _init_metadata(self):
        """Инициализирует метаданные профиля"""
        default_meta = {
            "user_agent": self._generate_user_agent(),
            "locale": random.choice(["en-US", "ru-RU", "fr-FR"]),
            "timezone": random.choice(["Europe/Moscow", "America/New_York"]),
            "screen_width": random.randint(1200, 1920),
            "screen_height": random.randint(800, 1080),
            "platform": random.choice(["Win32", "MacIntel"]),
            "created_at": datetime.now().isoformat()
        }

        try:
            if self.meta_file.exists():
                with open(self.meta_file, 'r', encoding='utf-8') as f:
                    saved_meta = json.load(f)
                    # Объединяем с дефолтными значениями
                    self.meta = {**default_meta, **saved_meta}
            else:
                self.meta = default_meta
                self._save_metadata()
        except Exception as e:
            logger.error(f"Metadata initialization failed: {e}")
            self.meta = default_meta

    def _save_metadata(self):
        """Сохраняет метаданные в файл"""
        try:
            with open(self.meta_file, 'w', encoding='utf-8') as f:
                json.dump(self.meta, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")

    def _generate_user_agent(self) -> str:
        """Генерирует User-Agent на основе платформы"""
        platform_map = {
            "Win32": "(Windows NT 10.0; Win64; x64)",
            "MacIntel": "(Macintosh; Intel Mac OS X 10_15_7)"
        }
        platform = self.meta.get("platform", "Win32")
        chrome_version = f"{random.randint(100, 115)}.0.{random.randint(1000, 9999)}.{random.randint(10, 99)}"
        return f"Mozilla/5.0 {platform_map.get(platform)} AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36"

    async def launch(self) -> BrowserContext:
        """Запуск браузера с оптимизированными stealth-настройками"""
        self.playwright = await async_playwright().start()
        logger.debug("Инициализация Playwright завершена")

        # Базовые настройки запуска
        launch_options = {
            "user_data_dir": str(self.profile_path),
            "headless": self.headless,
            "viewport": {
                "width": self.meta["screen_width"],
                "height": self.meta["screen_height"]
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
            "--disable-software-rasterizer"
        ]

        # Добавляем расширения если они есть
        if self.extensions:
            args.extend([
                f"--disable-extensions-except={','.join(self.extensions)}",
                f"--load-extension={','.join(self.extensions)}"
            ])

        # Добавляем прокси если есть
        if self.proxy:
            launch_options["proxy"] = {"server": self.proxy}

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
            self.tab_manager = TabManager(self.context)

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

            print("1234")
            logger.info(f"Launching {self.profile_name}")

            if actions_to_execute:
                for action in actions_to_execute:
                    try:
                        if action["action"] == "RabbyAuth":
                            print(f"RabbyAuth action: {action['action']}")
                            await RabbyAuth(self.context, self.tab_manager).authenticate()
                    except Exception as e:
                        logger.error(f"[{self.profile_name}] Action failed: {e}")
                        continue
            logger.info(f"Finished {self.profile_name}")
        except Exception as e:
            logger.error(f"[{self.profile_name}] Error: {e}")
            raise
        finally:
            await self.close()