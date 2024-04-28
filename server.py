import socketserver
import util.websockets
from util.router import Router
from util.request import Request
import util.router


class MyTCPHandler(socketserver.BaseRequestHandler):
    router = Router()
    router.add_all_routes()

    # It's suggested I make a different function to handle the infinite while loop and socket parsing
    # This function gets called after sending a response to a websocket, so after th sendall
    # Once in the loop, calls to .recv are assumed to be socket frames
    # Use sendall for sending frames over the connection
    #

    def handle(self):
        received_data = self.request.recv(2048)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)

        # Image stuff
        # if request.path.__contains__("image"):
        #     print("eagle")
        #     # Grab the length
        #     total_len = request.headers.get("Content-Length", 0)
        #     # If that length is greater than the buffer (2048)
        #     if int(total_len) > 2048:
        #         # Set an accumulator
        #         c_len = len(request.body)
        #
        #         # The cumulative data
        #         cumulative_data = received_data
        #         # While the accumulator is less than the total, buffer
        #         while c_len < int(total_len):
        #             received_data = self.request.recv(2048)
        #             print(self.client_address)
        #             print("--- received data ---")
        #             print(received_data)
        #             print("--- end of data ---\n\n")
        #
        #             # Append the new data to the byte array
        #             cumulative_data += received_data
        #             c_len += len(received_data)
        #
        #         # Remake the request with the rest of the bytes added
        #         request = Request(cumulative_data)
        #         send_me = self.router.route_request(request)
        #         self.request.sendall(send_me)
        # else:
        # websocket stuff
        if request.path == "/websocket":
            # compute and send the handshake
            userlist = []

            token = util.router.extract_token(request)
            username = util.router.extract_username(request)
            userlist.append(username)
            print(userlist)

            send_me = self.router.route_request(request)
            self.request.sendall(send_me)

            # loopin time
            print("handshake successful, time to buffer!")

            received_data = b''

            working_frame = bytearray()
            was_zero = False

            while True:
                if len(received_data) == 0:
                    received_data = self.request.recv(2048)
                    #rec_data = rec_data[4:]
                if len(received_data) > 0:
                    print("--- received data ---")
                    print(received_data)
                    print("--- end of data ---\n\n")

                    ws_frame = util.router.extract_ws_stuff(received_data)
                    print("fin bit = " + str(ws_frame.fin_bit))
                    print("opcode = " + str(ws_frame.opcode))

                    if ws_frame.fin_bit == 0 or was_zero:
                        # Buffer?
                        if len(ws_frame.payload) < ws_frame.payload_length:
                            payload = buffer_ws(ws_frame, self)
                            working_frame.extend(payload)
                        else:
                            working_frame.extend(ws_frame.payload)

                        if ws_frame.fin_bit == 0:
                            was_zero = True
                        else:
                            was_zero = False
                            send_me = util.router.handle_ws_message(working_frame, token)
                            self.request.sendall(send_me)
                            working_frame = bytearray()
                    else:
                        # Buffer?
                        if len(ws_frame.payload) < ws_frame.payload_length:
                            (payload, received_data) = buffer_ws(ws_frame, self)

                            send_me = util.router.handle_ws_message(payload, token)
                            self.request.sendall(send_me)
                        else:
                            send_me = util.router.handle_ws_message(ws_frame.payload, token)
                            self.request.sendall(send_me)
                            received_data = received_data[ws_frame.payload_length:]
        else:
            send_me = self.router.route_request(request)
            self.request.sendall(send_me)


# Helper function that just buffers and builds up a payload.
# Given a util.websockets.Frame and returns a payload to be sent.
def buffer_ws(ws: util.websockets.Frame, self: MyTCPHandler):
    # Set an accumulator
    total_len = ws.payload_length
    c_len = len(ws.payload)

    received_data = b''
    new_ws = util.websockets.Frame()

    # The cumulative data
    cumulative_data = bytearray(ws.payload)
    # While the accumulator is less than the total, buffer
    while c_len < int(total_len):
        received_data = self.request.recv(2048)
        new_ws = util.websockets.parse_ws_frame(received_data)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")

        # Append the new data to the byte array
        cumulative_data.extend(new_ws.payload)
        c_len += len(new_ws.payload)

    if len(received_data) > len(new_ws.payload):
        received_data = b''

    return cumulative_data, received_data

def main():
    host = "0.0.0.0"
    port = 8080

    # I was told to change "TCPServer" to "ThreadingTCPServer"
    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
