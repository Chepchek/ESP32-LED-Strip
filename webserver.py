import uasyncio as asyncio
import ujson


class WebServer:
    def __init__(self, effect_manager, ip_address, port=8080):  # Изменил порт на 8080 по умолчанию
        self.effect_manager = effect_manager
        self.ip_address = ip_address
        self.port = port
        self.server = None
        self.stop_event = asyncio.Event()

    async def start(self):
        self.server = await asyncio.start_server(self.handle_request, self.ip_address, self.port)
        print(f"Сервер запущен {self.ip_address}:{self.port}")
        async with self.server:
            await self.stop_event.wait()  # Ждет сигнала остановки
        print("Сервер остановлен")

    async def stop(self):
        self.stop_event.set()

    async def handle_request(self, reader, writer):
        """Асинхронная обработка входящего HTTP-запроса."""
        try:
            request_data = await reader.read(1024)
            request_data = request_data.decode()
            method, path, *_ = request_data.split('\r\n', 1)[0].split()
            response = await self.process_request(method, path, request_data)
            writer.write(response.encode())
            await writer.drain()
        except Exception as e:
            print(f"Ошибка обработки запроса: {e}")
            writer.write(b"HTTP/1.1 500 Internal Server Error\r\nContent-type: text/plain\r\n\r\nError")
            await writer.drain()

        finally:
            writer.close()
            await writer.wait_closed()

    async def process_request(self, method, path, request):
        """Обработка запроса, в зависимости от метода и пути."""
        if method == "GET" and path == "/":
            with open("templates/index.html", "r") as f:
                html_content = f.read()
            return f"HTTP/1.1 200 OK\r\nContent-type: text/html;charset=utf-8\r\n\r\n{html_content}"
        elif method == "GET" and path == "/effects":
            effects_data = []
            for effect_name, effect_class in self.effect_manager.effects.items():
                desc, params = effect_class.get_params_info()
                effects_data.append({
                    "name": effect_name[0].upper() + effect_name[1:],
                    "params": params,
                    "desc": desc  # Добавлено получение описания эффекта
                })
            response = ujson.dumps({"effects": effects_data})
            return f"HTTP/1.1 200 OK\r\nContent-type: application/json; charset=utf-8\r\n\r\n{response}"

        elif method == "POST" and path == "/start_effect":  # Изменено имя пути
            try:
                data = request.split('\r\n\r\n', 1)[1]
                params = ujson.loads(data)
                effect_name = params['effect']
                del params['effect']
                await self.effect_manager.handle_effect(effect_name, params)
                return "HTTP/1.1 200 OK\r\nContent-type: application/json; charset=utf-8\r\n\r\n{\"status\":\"OK\"}"  # Более корректный JSON
            except KeyError as e:
                return f"HTTP/1.1 400 Bad Request\r\nContent-type: application/json; charset=utf-8\r\n\r\n{{\"error\":\"Missing parameter: {e.args[0]}\"}}"  # Информативное сообщение
            except ValueError as e:
                return f"HTTP/1.1 400 Bad Request\r\nContent-type: application/json; charset=utf-8\r\n\r\n{{\"error\":\"Invalid JSON: {e}\"}}"  # Информативное сообщение
            except Exception as e:
                print(f"Ошибка сервера: {e}")
                return "HTTP/1.1 500 Internal Server Error\r\nContent-type: application/json; charset=utf-8\r\n\r\n{\"error\":\"Internal Server Error\"}"  # Более корректный JSON
        elif method == "POST" and path == "/stop_all":
            await self.effect_manager.stop_all()
            return f"HTTP/1.1 200 OK\r\nContent-type: application/json; charset=utf-8\r\n\r\n{{\"status\":\"OK\"}}"
        else:
            return "HTTP/1.1 404 Not Found\r\nContent-type: text/plain\r\n\r\nNot Found"
