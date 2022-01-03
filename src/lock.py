import socket
import socketserver
import threading

PORT = 53849
LOCATION = ("localhost", PORT)


def is_locked():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return s.connect_ex(LOCATION) == 0


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        pass


def lock():
    with socketserver.TCPServer(LOCATION, Handler) as server:
        threading.Thread(target=server.serve_forever)
