import uasyncio as asyncio
import ujson


class WebServer:
    def __init__(self, effect_manager, ip_address, port=8080):
        """
        Initializes a new instance of the WebServer class.

        Parameters:
            effect_manager: An instance responsible for managing LED effects.
            ip_address (str): The IP address on which the server will listen.
            port (int, optional): The port number on which the server will listen. Defaults to 8080.
        """
        self.effect_manager = effect_manager
        self.ip_address = ip_address
        self.port = port
        self.server = None
        self.stop_event = asyncio.Event()

    async def start(self):
        """
        Asynchronously starts the web server to listen for incoming connections.

        This function sets up the server to handle incoming HTTP requests on the specified
        IP address and port. It will continue to run until a stop signal is received.

        Returns:
            None: This function does not return a value. It runs the server until stopped.
        """
        self.server = await asyncio.start_server(self.handle_request, self.ip_address, self.port)
        print(f"Server start {self.ip_address}:{self.port}")
        async with self.server:
            await self.stop_event.wait()  # Ждет сигнала остановки
        print("Server stopped")

    async def stop(self):
        self.stop_event.set()

    async def handle_request(self, reader, writer):
        """
        Asynchronously handles an incoming HTTP request.

        This function reads the request data from the client, processes the request,
        and sends back an appropriate HTTP response.

        Parameters:
            reader (StreamReader): The stream reader object to read data from the client.
            writer (StreamWriter): The stream writer object to send data back to the client.

        Returns:
            None: This function does not return a value. It sends an HTTP response back to the client.
        """
        try:
            request_data = await reader.read(1024)
            request_data = request_data.decode()
            method, path, *_ = request_data.split('\r\n', 1)[0].split()
            response = await self.process_request(method, path, request_data)
            writer.write(response.encode())
            await writer.drain()
        except Exception as e:
            print(f"Request processing error: {e}")
            writer.write(b"HTTP/1.1 500 Internal Server Error\r\nContent-type: text/plain\r\n\r\nError")
            await writer.drain()

        finally:
            writer.close()
            await writer.wait_closed()

    async def process_request(self, method, path, request):
        """
        Processes an HTTP request based on the method and path.

        Parameters:
            method (str): The HTTP method of the request (e.g., 'GET', 'POST').
            path (str): The path of the request URL.
            request (str): The full HTTP request data as a string.

        Returns:
            str: An HTTP response string appropriate for the request, including headers and body.
        """
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
                    "desc": desc
                })
            response = ujson.dumps({"effects": effects_data})
            return f"HTTP/1.1 200 OK\r\nContent-type: application/json; charset=utf-8\r\n\r\n{response}"

        elif method == "POST" and path == "/start_effect":
            try:
                data = request.split('\r\n\r\n', 1)[1]
                params = ujson.loads(data)
                effect_name = params['effect']
                del params['effect']
                await self.effect_manager.handle_effect(effect_name, params)
                return "HTTP/1.1 200 OK\r\nContent-type: application/json; charset=utf-8\r\n\r\n{\"status\":\"OK\"}"
            except KeyError as e:
                return f"HTTP/1.1 400 Bad Request\r\nContent-type: application/json; charset=utf-8\r\n\r\n{{\"error\":\"Missing parameter: {e.args[0]}\"}}"
            except ValueError as e:
                return f"HTTP/1.1 400 Bad Request\r\nContent-type: application/json; charset=utf-8\r\n\r\n{{\"error\":\"Invalid JSON: {e}\"}}"
            except Exception as e:
                print(f"SERVER ERROR: {e}")
                return "HTTP/1.1 500 Internal Server Error\r\nContent-type: application/json; charset=utf-8\r\n\r\n{\"error\":\"Internal Server Error\"}"
        elif method == "POST" and path == "/stop_all":
            await self.effect_manager.stop_all()
            return f"HTTP/1.1 200 OK\r\nContent-type: application/json; charset=utf-8\r\n\r\n{{\"status\":\"OK\"}}"
        else:
            return "HTTP/1.1 404 Not Found\r\nContent-type: text/plain\r\n\r\nNot Found"
