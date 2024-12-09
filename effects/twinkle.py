import random

import uasyncio


class TwinkleEffect:
    """
    Инициализация эффекта "Мерцание".

    Args:
        strip: Объект светодиодной ленты. Должен поддерживать индексацию и метод write().
        params: Словарь параметров эффекта:
            - r: Красный компонент цвета (0-255, по умолчанию 255).
            - g: Зеленый компонент цвета (0-255, по умолчанию 255).
            - b: Синий компонент цвета (0-255, по умолчанию 255).
            - speed: Скорость мерцания (секунды, по умолчанию 0.2).
            - num_leds: Количество мерцающих светодиодов (по умолчанию 5).
    """

    def __init__(self, strip, params):
        self.strip = strip
        self.r, self.g, self.b = self._parse_params(params)
        self.speed = params.get('speed', 0.2)
        self.num_leds = params.get('num_leds', 5)  # количество мерцающих светодиодов
        self.intensity = params.get('intensity', 255)  # Новая настройка яркости, по умолчанию 255

    @staticmethod
    def _parse_params(params):
        r = int(params.get('r', 255))
        g = int(params.get('g', 255))
        b = int(params.get('b', 255))
        # Проверка значений на корректность (0-255)
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        return r, g, b

    async def run(self, stop_event):
        try:
            n = len(self.strip)
            while not stop_event.is_set():
                for i in range(self.num_leds):
                    led = random.randint(0, n - 1)
                    self.strip[led] = (
                        int(self.r * self.intensity / 255),
                        int(self.g * self.intensity / 255),
                        int(self.b * self.intensity / 255),
                    )
                await self.strip.write()
                await uasyncio.sleep(self.speed)
                for i in range(self.num_leds):
                    led = random.randint(0, n - 1)
                    self.strip[led] = (0, 0, 0)
                await self.strip.write()
                await uasyncio.sleep(self.speed)

        except Exception as e:
            print(f"Ошибка в эффекте Twinkle: {e}")
        finally:
            print("Эффект Twinkle остановлен")

    @staticmethod
    def get_params_info():
        return "Несколько светодиодов случайным образом мерцают",{
            "r": {"default": 255, "min": 0, "max": 255, "desc": "Красный компонент"},
            "g": {"default": 255, "min": 0, "max": 255, "desc": "Зеленый компонент"},
            "b": {"default": 255, "min": 0, "max": 255, "desc": "Синий компонент"},
            "speed": {"default": 0.2, "min": 0.01, "max": 1.0, "desc": "Скорость мерцания"},
            "num_leds": {"default": 5, "min": 1, "max": 60, "desc": "Количество мерцающих светодиодов"},
        }
