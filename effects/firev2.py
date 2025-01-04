import random

import uasyncio as asyncio


class FireEffectV2:
    """
    A class that implements a "fire" effect for an LED strip.

    This class uses a more complex algorithm than the previous version
    to create a more realistic fire effect on an LED strip.
    """

    def __init__(self, strip, params):
        """
        Initializes the fire effect for an LED strip using a more complex algorithm for a realistic effect.

        Parameters:
            strip: The LED strip object. It must support indexing and have a *write()* method.
            params: A dictionary of effect parameters:
                - r (int): Red color component (0-255, default is 255).
                - g (int): Green color component (0-255, default is 0).
                - b (int): Blue color component (0-255, default is 0).
                - intensity (float): Effect intensity (0.0-1.0, default is 0.5).
                - speed (float): Effect speed in seconds (default is 0.1).
                - cooling (int): Cooling rate (0-255, default is 50).
        """
        self.strip = strip
        self.n = len(self.strip)  # Number of LEDs
        self.r, self.g, self.b = self._parse_params(params)
        self.intensity = params.get('intensity', 128) / 255.0  # normalized to a range 0.0 to 1.0
        self.speed = params.get('speed', 0.1)
        self.cooling = int(params.get('cooling', 40))  # Affects the rate of attenuation
        self.heat = [0] * self.n  # Temperature array for each LED
        self.palette = self._generate_palette(self.r, self.g, self.b)  # Generating a color palette

    @staticmethod
    def _parse_params(params):
        """
        Parses and validates the color parameters from the given dictionary.

        Parameters:
            params (dict): A dictionary containing the color parameters with keys 'r', 'g', and 'b'.
                           Each key should map to an integer value between 0 and 255.

        Returns:
            tuple: A tuple containing the validated red, green, and blue components as integers.
                   Each component is clamped to the range 0-255.
        """
        r = max(0, min(255, int(params.get('r', 60))))
        g = max(0, min(255, int(params.get('g', 50))))
        b = max(0, min(255, int(params.get('b', 70))))
        return r, g, b

    @staticmethod
    def _generate_palette(r, g, b):
        """
        Generates a color palette based on the given RGB parameters.

        This method creates a list of 256 RGB color tuples, representing a gradient
        from black to the specified color.

        Parameters:
            r (int): The red component of the target color (0-255).
            g (int): The green component of the target color (0-255).
            b (int): The blue component of the target color (0-255).

        Returns:
            list: A list of 256 RGB color tuples, where each tuple contains three integers
                (r, g, b) representing the color values. The list starts with black (0, 0, 0)
                and gradually increases to the specified target color.
        """
        palette = []
        for i in range(256):
            r_val = int(r * (i / 255.0))
            g_val = int(g * (i / 255.0))
            b_val = int(b * (i / 255.0))
            palette.append((r_val, g_val, b_val))
        return palette

    async def run(self, stop_event):
        """
        Run the "fire" effect asynchronously.

        This method simulates a fire effect on the LED strip by manipulating heat values
        and translating them into colors. It runs continuously until the stop event is set.

        Parameters:
        -----------
        stop_event : asyncio.Event
            An event object used to stop the effect. The effect will continue running
            until this event is set.

        Notes:
        ------
        - The method uses the `heat` array to simulate temperature changes along the strip.
        - It adds random heat, simulates heat propagation and cooling, and maps temperatures to colors.
        - The effect is updated at intervals specified by `self.speed`.
        - Any exceptions during execution are caught and printed.
        - The method prints a message when the effect is stopped.
        """
        try:
            while not stop_event.is_set():
                # Adds heat to a random position on the LED strip.
                self.heat[random.randint(0, self.n - 1)] = int(255 * self.intensity)

                for i in range(self.n - 1, 0, -1):
                    decay = random.randint(0, self.cooling)
                    wave = random.randint(-10, 10)
                    self.heat[i] = max(0, min(255, int((self.heat[i] + self.heat[i - 1] + wave) * (1 - decay / 255.0))))

                # Convert temperature values to colors from the palette.
                for i in range(self.n):
                    color_index = int(self.heat[i] / 255.0 * len(self.palette))
                    color_index = max(0, min(len(self.palette) - 1, color_index))
                    self.strip[i] = self.palette[color_index]

                await self.strip.write()
                await asyncio.sleep(self.speed)

        except Exception as e:
            print(f"Error in Fire_v2: {e}")
        finally:
            print("Effect Fire_v2 stopped")

    def stop(self):
        """
        Stops the "fire" effect (not implemented in this version).
        """
        pass

    @staticmethod
    def get_params_info():
        """
        Returns information about the parameters required for the twinkle effect.

        Returns:
        - tuple: A tuple containing the description of the effect and a dictionary of parameter information.

        - str: The description of the effect ("FireV2").
        - dict: A dictionary where the keys are the parameter names and the values are dictionaries containing
                 information about each parameter.
        """
        return ("The FireEffectV2 class implements an advanced fire effect for LED strips. \
        It uses a complex algorithm to create a realistic, dynamic fire simulation.",
                {
                    "r": {"default": 255, "min": 0, "max": 255, "desc": "Red color"},
                    "g": {"default": 0, "min": 0, "max": 255, "desc": "Green color"},
                    "b": {"default": 0, "min": 0, "max": 255, "desc": "Blue color"},
                    "intensity": {"default": 0.5, "min": 0.0, "max": 1.0, "desc": "Intensity of the fire"},
                    "speed": {"default": 0.1, "min": 0.01, "max": 1.0, "desc": "Speed of the effect"},
                    "cooling": {"default": 50, "min": 0, "max": 255, "desc": "Cooling rate"},
                },)
