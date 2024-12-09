import network
import uasyncio

import effects
import webserver
import ws2812

# Настройка точки доступа
SSID = "WiFi_SSID"
PASSWORD = "password"  # Выберите надежный пароль

# Настройка светодиодной ленты
LED_COUNT = 180
PIN = 5
STRIP = ws2812.WS2812(PIN, LED_COUNT)


async def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        print("Connecting to WiFi...")
        await uasyncio.sleep(1)

    print(f"Connected to WiFi: {SSID}")
    print(f"IP address: {wlan.ifconfig()[0]}")
    return wlan.ifconfig()[0]


async def create_access_point():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=SSID, password=PASSWORD)
    print(f"Access Point '{SSID}' started")
    print(f"IP address: {ap.ifconfig()[0]}")
    return ap.ifconfig()[0]


async def main():
    stop_event = uasyncio.Event()  # создаем Event для остановки
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
    uasyncio.run(main())
