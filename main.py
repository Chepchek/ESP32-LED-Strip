import network
import uasyncio as asyncio

import effects
import webserver
import ws2812

# Wi-Fi data for connect or create  Access Point
SSID = "WiFi_SSID"
PASSWORD = "password"

# LED strip setting
LED_COUNT = 180
PIN = 5
STRIP = ws2812.WS2812(pin=PIN, pixel_count=LED_COUNT)


async def connect_to_wifi():
    """
    This function is used to connect to a Wi-Fi network using the provided SSID and password.

    Returns:
    str: The IP address of the connected Wi-Fi network.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        print("Connecting to WiFi...")
        await asyncio.sleep(1)

    print(f"Connected to WiFi: {SSID}")
    print(f"IP address: {wlan.ifconfig()[0]}")
    return wlan.ifconfig()[0]


async def create_access_point():
    """
    This function is used to create a Wi-Fi access point using the provided SSID and password.

    Parameters:
    None. This function uses the global SSID and PASSWORD variables.

    Returns:
    str: The IP address of the created Wi-Fi access point.
    """
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=SSID, password=PASSWORD)
    print(f"Access Point '{SSID}' started")
    print(f"IP address: {ap.ifconfig()[0]}")
    return ap.ifconfig()[0]


async def main():
    """
    This is the main function that orchestrates the LED strip effects and web server.

    The function creates an access point, starts the web server, and manages the LED strip effects.
    """
    stop_event = asyncio.Event()
    effect_manager = effects.EffectManager(STRIP, stop_event)
    ip_address = await create_access_point()

    try:
        web_server = webserver.WebServer(effect_manager, ip_address)
        await web_server.start()
    except KeyboardInterrupt:
        print("Stopping server...")
    finally:
        print('Server stopped')


if __name__ == "__main__":
    asyncio.run(main())
