# MicroPython code for controlling the LED strip
 - Add your improvements and interesting effects
## Known issues:
 - index.html it weighs too much
 - effects must correspond to some behavior described in already existing effects, perhaps an abstract class is needed, although you can just use existing ones as an example.

# Guide to creating an effect
  ##  1. Effect Class Structure:
  ### Each effect should be represented by a separate class. This class should contain:

**__init__(self, strip, params):** 
    `The constructor, initializing the effect object. It takes a strip object (representing the LED strip) and a params dictionary (effect parameters).`

**run(self, stop_event):** 
    `An asynchronous function that starts and runs the effect. It takes stop_event (a uasyncio.Event() object) used to interrupt the effect.`

~~**stop(self):** 
    `A function that stops the effect. Not implemented in the example but should be added for proper functionality. It might need to clean up resources or set a flag to indicate termination.`~~

**get_params_info(self):**
`A static function that returns information about the effect’s parameters (description and a dictionary with parameters).`
    
## 2. Parameter Parsing (_parse_params)
**The _parse_params function parses and validates parameters passed to the constructor. It’s crucial to validate input to prevent errors. The example checks RGB component values for the allowed range (0-255).**

Effect Logic (run)

* This is the most important part. The algorithm defining the effect’s behavior is implemented here. In the FireEffectV2 example:

* heat is an array storing “heat” for each LED.
* Heat is randomly added to a random position.
* Heat spreads along the strip, considering “cooling” (cooling).
* Heat values are converted to colors from the palette.
* Data is sent to the strip using strip.write().
* uasyncio.sleep(self.speed) provides a pause between updates.

Error Handling

Exception handling (try...except) prevents program crashes due to errors.

# Example of Creating a New Effect (Blinking)

Let’s create a simple blinking effect:

```Python
import uasyncio as asyncio


class BlinkEffect:
    def __init__(self, strip, params):
        self.strip = strip
        self.r = int(params.get('r', 255))
        self.g = int(params.get('g', 255))
        self.b = int(params.get('b', 255))
        self.speed = params.get('speed', 0.5)
        self.on = True

    async def run(self, stop_event):
        try:
            while not stop_event.is_set():
                color = (self.r, self.g, self.b) if self.on else (0, 0, 0)
                self.strip.fill(color)
                await self.strip.write()
                await asyncio.sleep(self.speed)
                self.on = not self.on
        except Exception as e:
            print(f"Error in Blink effect: {e}")
        finally:
            print("Blink effect stopped")

    def stop(self):
        pass

    @staticmethod
    def get_params_info():
        return ("Simple blinking effect", # Short description of the effect
                # Parameter of the effect
                {
                    "r": {"default": 255, "min": 0, "max": 255, "desc": "Red component"},
                    "g": {"default": 255, "min": 0, "max": 255, "desc": "Green component"},
                    "b": {"default": 255, "min": 0, "max": 255, "desc": "Blue component"},
                    "speed": {"default": 0.5, "min": 0.1, "max": 2.0, "desc": "Blinking speed"},
                })
```


# Running the Effect:
### Add this class to the EffectsManager class for dynamic loading on the site
```Python
class EffectManager:

    def __init__(self, strip, stop_event):
        self.strip = strip
        self.effects = {
            "fire_v2": FireEffectV2,
            "twinkle": TwinkleEffect,
            "strobe": StrobeEffect,
                        <-- add here your effect class like this "EffectName": EffectClass
        }
```
### Download it to the board and reboot... DONE!
