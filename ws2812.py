import machine
import neopixel
import uasyncio as asyncio


class WS2812:
    def __init__(self, pin: int, pixel_count: int):
        """
        Initialize the WS2812 LED strip.

        Args:
            pin (int): The number of the GPIO pin to which the LED strip is connected.
            pixel_count (int): The number of pixels in the LED strip.
        """
        self.np = neopixel.NeoPixel(machine.Pin(pin), pixel_count)
        self._write_lock = asyncio.Lock()  # Mutex for protecting write()

    async def write(self):
        """
        Write the pixel data to the LED strip.

        This method is async to allow for non-blocking writes.
        A lock is used to prevent data races when writing to the strip.
        """
        async with self._write_lock:  # Lock to prevent data races
            self.np.write()

    def fill(self, color):
        """
        Fill the entire LED strip with a single color.

        Args:
            color (tuple): The RGB color to fill the strip with.
        """
        self.np.fill(color)

    def set_pixel(self, pixel: int, color: tuple):
        """
        Set the color of a single pixel.

        Args:
            pixel (int): The index of the pixel to set.
            color (tuple): The RGB color to set the pixel to.

        If the pixel index is out of range, an error message is printed and the method returns early.
        """
        if pixel >= len(self.np):
            print(f"Invalid pixel value {pixel} >= {len(self.np)}")
            return
        self.np[pixel] = color

    def __getitem__(self, key):
        """
        Get the color of a single pixel.

        Args:
            key (int): The index of the pixel to get.

        Returns:
            tuple: The RGB color of the pixel.
        """
        return self.np[key]

    def __setitem__(self, key, value):
        """
        Set the color of a single pixel.

        Args:
            key (int): The index of the pixel to set.
            value (tuple): The RGB color to set the pixel to.
        """
        self.np[key] = value

    def __len__(self):
        """
        Get the number of pixels in the LED strip.

        Returns:
            int: The number of pixels in the strip.
        """
        return len(self.np)
