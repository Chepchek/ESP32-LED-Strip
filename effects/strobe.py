import uasyncio


class StrobeEffect:
    """
       Инициализация эффекта "Стробоскоп".

       Args:
           strip: Объект светодиодной ленты. Должен поддерживать индексацию и метод write().
           params: Словарь параметров эффекта:
               - r: Красный компонент цвета (0-255, по умолчанию 255).
               - g: Зеленый компонент цвета (0-255, по умолчанию 255).
               - b: Синий компонент цвета (0-255, по умолчанию 255).
               - speed: Скорость стробоскопа (секунды, по умолчанию 0.1).
               - delay: Задержка между вспышками (секунды, по умолчанию 0.2).
               - intensity: Интенсивность вспышек (0-255, по умолчанию 255).

       """

    def __init__(self, strip, params):
        self.strip = strip
        self.r, self.g, self.b = self._parse_params(params)
        self.speed = params.get('speed', 0.1)
        self.delay = params.get('delay', 0.2)
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
                for i in range(n):
                    self.strip[i] = (
                        int(self.r * self.intensity / 255),
                        int(self.g * self.intensity / 255),
                        int(self.b * self.intensity / 255),
                    )
                await self.strip.write()
                await uasyncio.sleep(self.delay)
                for i in range(n):
                    self.strip[i] = (0, 0, 0)
                await self.strip.write()
                await uasyncio.sleep(self.speed)
        except Exception as e:
            print(f"Ошибка в эффекте Strobe: {e}")
        finally:
            print("Эффект Strobe остановлен")

    @staticmethod
    def get_params_info():
        """
        Возвращает информацию о параметрах эффекта "Стробоскоп".

        Returns:
            tuple: Кортеж, содержащий текстовое описание эффекта и словарь параметров.

            - str: Текстовое описание эффекта ("Стробоскоп").
            - dict: Словарь, ключи которого - названия параметров, а значения - словари с информацией о параметрах:
                - "default": значение по умолчанию.
                - "min": минимальное значение.
                - "max": максимальное значение.
                - "desc": текстовое описание параметра.
        """
        return "Стробоскоп", {
            "r": {"default": 255, "min": 0, "max": 255, "desc": "Красный компонент"},
            "g": {"default": 255, "min": 0, "max": 255, "desc": "Зеленый компонент"},
            "b": {"default": 255, "min": 0, "max": 255, "desc": "Синий компонент"},
            "speed": {"default": 0.1, "min": 0.01, "max": 1.0, "desc": "Скорость стробоскопа"},
            "delay": {"default": 0.2, "min": 0.01, "max": 1.0, "desc": "Задержка между вспышками"},
            "intensity": {"default": 255, "min": 0, "max": 255, "desc": "Интенсивность вспышек"},
        }
