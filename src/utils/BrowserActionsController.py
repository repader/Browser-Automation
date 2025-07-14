import asyncio
import time
import tracemalloc
from datetime import datetime
import random
from typing import Optional, Union

from playwright.async_api import BrowserContext, Page, Locator

tracemalloc.start()
class BrowserActionsController:
    def __init__(self, context: BrowserContext):
        self.context = context
        self.page: Optional[Page] = None
        self.session_start = datetime.now()
        self.activity_history = []

        self.max_session_minutes = 30
        self.min_interaction_delay = 5
        self.max_interaction_delay = 15

        self.min_delay = 0.1
        self.max_delay = 2.0
        self.scroll_step_min = 100
        self.scroll_step_max = 500
        self.typing_speed_min = 0.05
        self.typing_speed_max = 0.3



    async def random_delay(self, min_sec: Optional[float] = None, max_sec: Optional[float] = None) -> None:
        """Случайная задержка между действиями"""
        min_val = min_sec if min_sec is not None else self.min_delay
        max_val = max_sec if min_sec is not None else self.max_delay
        await asyncio.sleep(random.uniform(min_val, max_val))

    async def click(self, selector: Union[str, Locator], move_steps: int = 30) -> None:
        """Клик по элемену"""
        self.page = await self.get_current_page()
        element = selector if isinstance(selector, Locator) else await self.page.selector(selector)
        await element.scroll_into_view_if_needed()

        box = await element.bounding_box()
        if not box:
            raise ValueError("Element not visible or not found")

        await self.page.mouse.move(
            box['x'] + box['width'] / 2,
            box['y'] + box['height'] / 2,
            steps=random.randint(move_steps // 2, move_steps * 2)
        )

        await self.page.mouse.down()
        await self.random_delay(0.05, 0.2)
        await self.page.mouse.up()

    async def typing(self, selector: Union[str, Locator], text: str, error_probably: float = 0.03) -> None:
        """Ввод текста"""
        self.page = await self.get_current_page()
        element = selector if isinstance(selector, Locator) else await self.page.selector(selector)
        await self.click(element)

        for char in text:
            await element.press(char)
            await self.random_delay(self.typing_speed_min, self.typing_speed_max)

            if random.random() < error_probably:
                for _ in range(random.randint(1,3)):
                    await element.press('Backspace')
                    await self.random_delay(0.1, 0.3)

                for correct_char in char:
                    await element.press(correct_char)

                    await self.random_delay(self.typing_speed_min, self.typing_speed_max)

    async def scroll(self, scroll_times: Optional[int] = None) -> None:
        self.page = await self.get_current_page()
        """Прокрутка страницы"""
        if scroll_times is None:
            scroll_times = random.randint(2, 5)

        for _ in range(scroll_times):

            method = random.choice([
                lambda: self.page.mouse.wheel(0, random.randint(self.scroll_step_min, self.scroll_step_max)),
                lambda: self.page.keyboard.press('PageDown')
            ])

            method()
            await self.random_delay(0.5, 1.5)

    async def random_mouse_movement(self, moves: int = 3) -> None:
        self.page = await self.get_current_page()
        """Случайные движения мыши по странице"""
        viewport = self.page.viewport_size
        if not viewport:
            return
        for _ in range(moves):
            x = random.randint(0, viewport['width'] - 1)
            y = random.randint(0, viewport['height'] - 1)
            await self.page.mouse.move(x, y, steps=random.randint(10, 30))
            await self.random_delay(0.2, 0.8)

    async def navigate(self, url: str) -> Page:

        """Переход на страницу"""
        new_page = await self.context.new_page()
        await new_page.goto(url)
        for page in self.context.pages:
            if not page.is_closed() and not page == new_page:
                await page.close()

        await self.random_delay(1.5, 4.0)

        await self.random_mouse_movement(random.randint(1, 3))

        return new_page

    async def _add_activity(self, action: str):
        """Логирование действий"""
        self.activity_history.append({
            'time': datetime.now(),
            'action': action
        })

    async def perform_random_actions(self, actions_count: int = 2) -> None:
        self.page = await self.get_current_page()
        """Выполнение случайных действий"""
        actions = [
            self.random_mouse_movement,
            self.scroll,
            lambda: self.page.keyboard.press('Tab'),
            lambda: self.click('body')  # Клик в случайное место
        ]

        for _ in range(actions_count):
            random.choice(actions)(1)
            await self.random_delay(0.5, 1.5)

    async def emulate_real_session(self):
        """Имитация реального времени сессии с паузами"""
        session_duration = random.randint(5, self.max_session_minutes)
        start_time = time.time()

        while (time.time() - start_time) < session_duration * 60:
            actions = [
                lambda: self.scroll(random.randint(1, 3)),
                lambda: self.random_mouse_movement(random.randint(1, 3)),
                lambda: self.perform_random_actions(1),
                lambda: self.random_delay(self.min_interaction_delay, self.max_interaction_delay)
            ]

            action = random.choice(actions)
            action()

            await self._add_activity(action.__name__ if hasattr(action, '__name__') else str(action))

    async def solve_possible_captcha(self):
        self.page = await self.get_current_page()
        """Попытка решения капчи"""
        if self.page.is_visible('iframe[src*="captcha"]'):
            await self._add_activity('Captcha detected - trying to solve')

            # Здесь должна быть интеграция с API решения капч

            await self.random_delay(5, 10)
            return True
        return False

    async def get_current_page(self) -> Optional[Page]:
        """Возвращает текущую активную страницу (если есть)"""
        pages = self.context.pages
        return pages[-1] if pages else None

    async def get_current_page_url(self):
        page = await self.get_current_page()
        return page.url if page else None