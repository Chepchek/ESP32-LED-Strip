import random

import uasyncio as asyncio


class TwinkleEffect:

    def __init__(self, strip, params):
        """
        Initialize a TwinkleEffect instance.

        Parameters:
        - strip: An object representing the LED strip. It should have a method 'write' to update the strip.
        - params: A dictionary containing the parameters for the effect.
                  The dictionary should contain the following keys:
                  - 'r': Red component of the color (default: 60).
                  - 'g': Green component of the color (default: 50).
                  - 'b': Blue component of the color (default: 70).
                  - 'speed': Speed of the twinkling effect (default: 0.2, range: 0.01-1.0).
                  - 'num_leds': Number of LEDs to twinkle (default: 5, range: 1-60).
                  - 'intensity': Intensity of the twinkling effect (default: 255).

        Returns:
        - None
        """
        self.strip = strip
        self.r, self.g, self.b = self._parse_params(params)
        self.speed = params.get('speed', 0.2)
        self.num_leds = params.get('num_leds', 5)  # number of flickering LEDs
        self.intensity = params.get('intensity', 255)

    @staticmethod
    def _parse_params(params):
        """
        Parses and validates the color parameters from the given dictionary.

        Parameters:
        - params (dict): A dictionary containing the color parameters with keys 'r', 'g', and 'b'.
                         Each key should map to an integer value between 0 and 255.

        Returns:
        - tuple: A tuple containing the validated red, green, and blue components as integers.
                 Each component is clamped to the range 0-255.
        """
        r = max(0, min(255, int(params.get('r', 60))))
        g = max(0, min(255, int(params.get('g', 50))))
        b = max(0, min(255, int(params.get('b', 70))))
        return r, g, b

    async def run(self, stop_event):
        """
        This function runs the twinkling effect on the LED strip.

        Parameters:
        - stop_event (Event): An asyncio event that is set to stop the effect.

        The function continuously updates the LED strip to create a twinkling effect.
        It randomly selects LEDs to light up and dim them over time, controlled by the parameters.
        If an exception occurs during the execution, it prints an error message and stops the effect.
        """
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
                await asyncio.sleep(self.speed)
                for i in range(self.num_leds):
                    led = random.randint(0, n - 1)
                    self.strip[led] = (0, 0, 0)
                await self.strip.write()
                await asyncio.sleep(self.speed)

        except Exception as e:
            print(f"Error in Twinkle: {e}")
        finally:
            print("Effect Strobe stopped")

    @staticmethod
    def get_params_info():
        """
        Returns information about the parameters required for the twinkle effect.

        Returns:
        - tuple: A tuple containing the description of the effect and a dictionary of parameter information.

        - str: The description of the effect ("Twinkle").
        - dict: A dictionary where the keys are the parameter names and the values are dictionaries containing
                 information about each parameter.
        """
        return ("Several LEDs flicker randomly", {
            "r": {"default": 255, "min": 0, "max": 255, "desc": "Red color"},
            "g": {"default": 255, "min": 0, "max": 255, "desc": "Green color"},
            "b": {"default": 255, "min": 0, "max": 255, "desc": "Blue color"},
            "speed": {"default": 0.2, "min": 0.01, "max": 1.0, "desc": "Flickering speed"},
            "num_leds": {"default": 5, "min": 1, "max": 60, "desc": "Number of flickering LEDs"},
        })
