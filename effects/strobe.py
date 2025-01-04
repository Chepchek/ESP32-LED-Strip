import uasyncio as asyncio


class StrobeEffect:
    """
    A class representing a strobe effect for an LED strip.

    """

    def __init__(self, strip, params):
        """
        Initializes the StrobeEffect object.

        Parameters:
        - strip: The LED strip object. This object is responsible for controlling the LED strip.
        - params: A dictionary containing the parameters for the effect. The dictionary may contain the following keys:
                  'r': The red component of the color (default is 60).
                  'g': The green component of the color (default is 50).
                  'b': The blue component of the color (default is 70).
                  'speed': The speed of the strobe effect (default is 0.1, range: 0.01 to 1.0).
                  'delay': The delay between strobe pulses (default is 0.2, range: 0.01 to 1.0).
                  'intensity': The intensity of the strobe pulses (default is 255, range: 0 to 255).
        """
        self.strip = strip
        self.r, self.g, self.b = self._parse_params(params)
        self.speed = params.get('speed', 0.1)
        self.delay = params.get('delay', 0.2)
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
        Runs the strobe effect asynchronously.

        Parameters:
        - stop_event: An event object to stop the effect.

        Exceptions:
        - Any exceptions that occur during the effect will be printed.
        """
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
                await asyncio.sleep(self.delay)
                for i in range(n):
                    self.strip[i] = (0, 0, 0)
                await self.strip.write()
                await asyncio.sleep(self.speed)
        except Exception as e:
            print(f"Error in Strobe: {e}")
        finally:
            print("Effect Strobe stopped")

    @staticmethod
    def get_params_info():
        """
        Returns information about the parameters of the strobe effect.

        Returns:
        - tuple: A tuple containing the description of the effect and a dictionary of parameter information.

        - str: The description of the effect ("Strobe").
        - dict: A dictionary where the keys are the parameter names and the values are dictionaries containing
                 information about each parameter.
        """
        return ("Strobe", {
            "r": {"default": 255, "min": 0, "max": 255, "desc": "Red color"},
            "g": {"default": 255, "min": 0, "max": 255, "desc": "Green color"},
            "b": {"default": 255, "min": 0, "max": 255, "desc": "Blue color"},
            "speed": {"default": 0.1, "min": 0.01, "max": 1.0, "desc": "Strobe speed"},
            "delay": {"default": 0.2, "min": 0.01, "max": 1.0, "desc": "Delay between pulses"},
            "intensity": {"default": 255, "min": 0, "max": 255, "desc": "Pulse intensity"},
        })
