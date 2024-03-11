import array
import json
import random
import socketserver
from util.request import Request
import uuid
from util.router import Router

class MyTCPHandler(socketserver.BaseRequestHandler):

    router = Router()
    router.add_all_routes()


    def handle(self):
        received_data = self.request.recv(2048)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)
        send_me = self.router.route_request(request)
        self.request.sendall(send_me)


def main():
    host = "0.0.0.0"
    port = 8080

    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.TCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))

    server.serve_forever()


if __name__ == "__main__":
    main()
