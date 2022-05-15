from time import sleep
import socketserver


class TCPHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

        # Custom Handler parameters
        self.data = None

    def handle(self) -> None:
        self.data = self.request.recv(1024).strip()
        print(f"{self.client_address[0]} wrote: {self.data}")
        sleep(3)
        self.request.sendall(b"Back from the server")



HOST = "localhost"
PORT = 9999
with socketserver.TCPServer((HOST, PORT), TCPHandler) as server:
    server.serve_forever()