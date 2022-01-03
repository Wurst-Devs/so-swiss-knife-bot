import socket
import socketserver
import asyncio

PORT = 53849
LOCATION = ('localhost', PORT)

def is_locked():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return s.connect_ex(LOCATION) == 0

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.request.sendall(self.data)

class Lock:
    def __init__(
        self,
    ):
        self.loop = asyncio.get_event_loop()

    def start(self):
        asyncio.run_coroutine_threadsafe(self.process(), self.loop)
    
    async def process(self):
        with socketserver.TCPServer(LOCATION, Handler) as server:
            server.serve_forever()
