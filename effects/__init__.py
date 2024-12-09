import uasyncio as asyncio

from .fire import FireEffect
from .firev2 import FireEffectV2
from .rainbow import RainbowEffect
from .strobe import StrobeEffect
from .twinkle import TwinkleEffect


class EffectManager:
    """
    Класс для управления различными эффектами для светодиодной ленты.
    """

    def __init__(self, strip, stop_event):
        """
        Инициализация EffectManager.

        Args:
            strip: Объект светодиодной ленты.
            stop_event: Событие для остановки всех эффектов.
        """
        self.strip = strip
        self.effects = {
            "fire": FireEffect,
            "fire_v2": FireEffectV2,
            "rainbow": RainbowEffect,
            "twinkle": TwinkleEffect,
            "strobe": StrobeEffect,
        }
        self.current_effect_task = None  # Задача текущего эффекта
        self.lock = asyncio.Lock()  # Мьютекс для синхронизации
        self.stop_event = stop_event  # используем переданное событие

    async def stop_all(self):
        """Остановить все запущенные эффекты."""
        if self.current_effect_task:
            print("Останавливаем текущий эффект...")
            self.stop_event.set()
            self.current_effect_task.cancel()
            self.current_effect_task = None  # Сброс задачи сразу, чтобы не блокировать lock
            self.stop_event.clear()  # сбрасываем событие
            print("Текущий эффект остановлен.")
        await self.turn_off_strip()

    async def turn_off_strip(self):
        """Выключить светодиодную ленту."""
        for i in range(len(self.strip)):  # Выключаем ленту
            self.strip[i] = (0, 0, 0)
        await self.strip.write()

    async def handle_effect(self, effect_name, params):
        """
        Обработка запроса на запуск эффекта.
        """
        async with self.lock:
            if self.current_effect_task:
                print("Останавливаем текущий эффект...")
                self.stop_event.set()
                self.current_effect_task.cancel()
                self.current_effect_task = None  # Сброс задачи сразу, чтобы не блокировать lock
                self.stop_event.clear()  # сбрасываем событие
                print("Текущий эффект остановлен.")

            if effect_name.lower() in self.effects:
                effect_class = self.effects[effect_name.lower()]
                print(f"Запуск эффекта: {effect_class.__name__}...")
                try:
                    self.current_effect_task = asyncio.create_task(
                        effect_class(self.strip, params).run(self.stop_event)
                    )
                except Exception as e:
                    print(f"Ошибка при запуске эффекта: {e}")
                    self.current_effect_task = None
            else:
                print(f"Эффект '{effect_name} | {self.effects}' не найден.")
