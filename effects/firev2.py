import random

import uasyncio


class FireEffectV2:
    """
    Класс, реализующий эффект "огонь" для светодиодной ленты.  Использует более сложный алгоритм,
    чем предыдущая версия, для создания более реалистичного эффекта.
    """

    def __init__(self, strip, params):
        """
        Инициализация эффекта.

        Args:
            strip: Объект светодиодной ленты.  Должен поддерживать индексацию и метод write().
            params: Словарь параметров эффекта:
                - r: Красный компонент цвета (0-255, по умолчанию 255).
                - g: Зеленый компонент цвета (0-255, по умолчанию 0).
                - b: Синий компонент цвета (0-255, по умолчанию 0).
                - intensity: Интенсивность эффекта (0.0-1.0, по умолчанию 0.5).
                - speed: Скорость эффекта (секунды, по умолчанию 0.1).
                - cooling: Скорость охлаждения (0-255, по умолчанию 50).
        """
        self.strip = strip
        self.n = len(self.strip)  # Количество светодиодов
        self.r, self.g, self.b = self._parse_params(params)  # Разбор и проверка параметров цвета
        self.intensity = params.get('intensity', 128) / 255.0  # Нормализация интенсивности к диапазону 0.0-1.0
        self.speed = params.get('speed', 0.1)  # Скорость обновления эффекта
        self.cooling = int(params.get('cooling', 40))  # Параметр охлаждения (влияет на скорость затухания)
        self.heat = [0] * self.n  # Массив температур для каждого светодиода
        self.palette = self._generate_palette(self.r, self.g, self.b)  # Генерация цветовой палитры

    @staticmethod
    def _parse_params(params):
        """Разбирает и проверяет параметры цвета."""
        r = int(params.get('r', 255))
        g = int(params.get('g', 0))
        b = int(params.get('b', 0))
        # Проверка значений на корректность (0-255)
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        return r, g, b

    @staticmethod
    def _generate_palette(r, g, b):
        """Генерирует цветовую палитру на основе заданных параметров RGB."""
        palette = []
        for i in range(256):
            r_val = int(r * (i / 255.0))
            g_val = int(g * (i / 255.0))
            b_val = int(b * (i / 255.0))
            palette.append((r_val, g_val, b_val))
        return palette

    async def run(self, stop_event):
        """
        Запуск эффекта "огонь".  Асинхронная функция.

        Args:
            stop_event:  Событие, используемое для остановки эффекта (должен быть объектом, объект uasyncio.Event()).
        """
        try:
            while not stop_event.is_set():  # Цикл работает до тех пор, пока не установлен флаг остановки
                # Добавление тепла в случайную позицию на ленте
                self.heat[random.randint(0, self.n - 1)] = int(255 * self.intensity)

                # Распространение тепла и охлаждение вдоль ленты
                for i in range(self.n - 1, 0, -1):
                    decay = random.randint(0, self.cooling)  # Случайное значение спада тепла
                    wave = random.randint(-10, 10)  # Случайная волна для добавления динамики
                    self.heat[i] = max(0, min(255, int((self.heat[i] + self.heat[i - 1] + wave) * (1 - decay / 255.0))))

                # Преобразование значений температуры в цвета из палитры
                for i in range(self.n):
                    color_index = int(self.heat[i] / 255.0 * len(self.palette))  # Исправлено: убрали -1
                    color_index = max(0, min(len(self.palette) - 1, color_index))  # проверка границ индекса
                    self.strip[i] = self.palette[color_index]

                await self.strip.write()  # Отправка данных на светодиодную ленту
                await uasyncio.sleep(self.speed)  # Пауза

        except Exception as e:
            print(f"Ошибка в эффекте Fire_v2: {e}")
        finally:
            print("Эффект Fire_v2 остановлен")

    def stop(self):
        """Метод остановки эффекта (пока не реализован)."""
        pass

    @staticmethod
    def get_params_info():
        return "Эффект имитирует пламя\nИспользует более сложный алгоритм, \
        чем предыдущая версия, для создания более реалистичного эффекта.", {
            "r": {"default": 255, "min": 0, "max": 255, "desc": "Красный компонент"},
            "g": {"default": 0, "min": 0, "max": 255, "desc": "Зеленый компонент"},
            "b": {"default": 0, "min": 0, "max": 255, "desc": "Синий компонент"},
            "intensity": {"default": 0.5, "min": 0.0, "max": 1.0, "desc": "Яркость"},
            "speed": {"default": 0.1, "min": 0.01, "max": 1.0, "desc": "Скорость"},
            "cooling": {"default": 50, "min": 0, "max": 255, "desc": "Охлаждение"},
        },
