import uasyncio as asyncio

from .firev2 import FireEffectV2
from .strobe import StrobeEffect
from .twinkle import TwinkleEffect


class EffectManager:

    def __init__(self, strip, stop_event):
        """
        Initialize the EffectManager class.

        Parameters:
        - strip: An instance of the LED strip driver.
        - stop_event: An asyncio Event object used to signal the stop of the current effect.

        The EffectManager class manages and handles different LED strip effects.
        It initializes the LED strip driver, a dictionary of available effects,
        a task for the current effect, an asyncio Lock, and an asyncio Event.
        """
        self.strip = strip
        self.effects = {
            "fire_v2": FireEffectV2,
            "twinkle": TwinkleEffect,
            "strobe": StrobeEffect,
        }
        self.current_effect_task = None
        self.lock = asyncio.Lock()
        self.stop_event = stop_event

    async def stop_all(self):
        """
        Stop all running effects and turn off the LED strip.
        """
        if self.current_effect_task:
            print("Stopping the current effect...")
            self.stop_event.set()
            self.current_effect_task.cancel()
            self.current_effect_task = None
            self.stop_event.clear()
            print("The current effect is stopped.")
        await self.turn_off_strip()

    async def turn_off_strip(self):
        """
        Turn off the LED strip by setting all LEDs to black (0, 0, 0) and writing the changes to the strip.
        """
        for i in range(len(self.strip)):
            self.strip[i] = (0, 0, 0)
        await self.strip.write()

        
    async def handle_effect(self, effect_name, params):
        """
        Manages and handles different LED strip effects.

        Parameters:
            effect_name (str): The name of the effect to be started.
            params (dict): Additional parameters required for the effect.

        This function handles the starting and stopping of different LED strip effects.
        It ensures that only one effect is running at a time by using an asyncio Lock.
        If a new effect is requested while another effect is running, the current effect is stopped.
        If the requested effect is not found, an appropriate message is printed.
        """
        async with self.lock:
            if self.current_effect_task:
                print("Stopping the current effect...")
                self.stop_event.set()
                self.current_effect_task.cancel()
                self.current_effect_task = None  # Reset the task immediately to avoid blocking the lock
                self.stop_event.clear()  # Clear the event
                print("The current effect is stopped.")

            if effect_name.lower() in self.effects:
                effect_class = self.effects[effect_name.lower()]
                print(f"{effect_class.__name__} Startup...")
                try:
                    self.current_effect_task = asyncio.create_task(
                        effect_class(self.strip, params).run(self.stop_event)
                    )
                except Exception as e:
                    print(f"Error when starting the effect: {effect_class.__name__}\n{e}")
                    self.current_effect_task = None
            else:
                print(f"The effect '{effect_name} | {self.effects}' was not found.")
