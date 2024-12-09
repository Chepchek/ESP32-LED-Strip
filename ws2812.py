import machine
import neopixel
import uasyncio as asyncio


class WS2812:
    def __init__(self, pin, pixel_count: int):
        self.np = neopixel.NeoPixel(machine.Pin(pin), pixel_count)
        self._write_lock = asyncio.Lock()  # Добавляем мьютекс для защиты write()

    async def write(self):
        async with self._write_lock:  # Блокируем доступ к write() для предотвращения гонки данных
            self.np.write()

    def fill(self, color):
        self.np.fill(color)

    def set_pixel(self, pixel: int, color: tuple):
        if pixel >= len(self.np):
            print(f"Invalid pixel value {pixel} >= {len(self.np)}")
            return
        self.np[pixel] = color

    def __getitem__(self, key):
        return self.np[key]

    def __setitem__(self, key, value):
        self.np[key] = value

    def __len__(self):
        return len(self.np)
