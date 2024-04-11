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

        # Grab the length
        total_len = request.headers.get("Content-Length", 0)
        #print(total_len)
        # If that length is greater than the buffer (2048)
        if int(total_len) > 2048:
            # Set an accumulator
            c_len = len(request.body)

            # The cumulative data
            cumulative_data = received_data
            # While the accumulator is less than the total, buffer
            while c_len < int(total_len):

                #print("total_len = " + str(total_len))
                #print("c_len = " + str(c_len))

                received_data = self.request.recv(2048)
                print(self.client_address)
                print("--- received data ---")
                print(received_data)
                print("--- end of data ---\n\n")

                # Append the new data to the byte array
                cumulative_data += received_data
                c_len += len(received_data)
                #print("c_len now = " + str(c_len))



            # Remake the request with the rest of the bytes added
            print(cumulative_data)
            request = Request(cumulative_data)

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
