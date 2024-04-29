import json
import socketserver
import util.websockets
from util.router import Router
from util.request import Request
import util.router

test = []
userlist = []


class MyTCPHandler(socketserver.BaseRequestHandler):
    router = Router()
    router.add_all_routes()

    # It's suggested I make a different function to handle the infinite while loop and socket parsing
    # This function gets called after sending a response to a websocket, so after th sendall
    # Once in the loop, calls to .recv are assumed to be socket frames
    # Use sendall for sending frames over the connection

    def handle(self):
        received_data = self.request.recv(2048)
        global userlist

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

        if request.path == "/users":
            # print("users are: " + str(userlist))
            to_send = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: application/json\r\nContent-Length: LEN\r\n\r\n"

            # losing my mind
            lista_de_users = []
            for user in userlist:
                lista_de_users.append({"username": user})

            json_data = json.dumps(lista_de_users)
            e_json = json_data.encode()
            j_len = len(e_json)
            send = to_send.replace("LEN", j_len.__str__())
            add_to = send.encode()

            send_me = add_to + e_json

            self.request.sendall(send_me)


        if request.path == "/websocket":
            # compute and send the handshake

            global test
            #print("new connection")
            if not test.__contains__(self):
                test.append(self)

            token = util.router.extract_token(request)
            username = util.router.extract_username(request)

            if username != "Guest" and (not userlist.__contains__(username)):
                userlist.append(username)

            #print(userlist)

            send_me = self.router.route_request(request)
            self.request.sendall(send_me)

            # loopin time
            #print("handshake successful, time to buffer!")

            working_frame = bytearray()
            was_zero = False

            while True:

                received_data = self.request.recv(2)

                if len(received_data) > 0:
                    # print("--- received data ---")
                    # print(received_data)
                    # print("--- end of data ---\n\n")

                    fin_bit = (received_data[0] & 0b10000000) >> 7  # 0 >> 7 = 0, 128 (256?) >> 7 = 1
                    #print("fin_bit = " + str(fin_bit))
                    opcode = (received_data[0] & 0b00001111)
                    #print("opcode = " + str(opcode))

                    if opcode == 8:
                        userlist.remove(username)
                        break

                    masking_bit = received_data[1] & 0b10000000  # either 0 or 128
                    #print("masking bit = " + str(masking_bit))
                    pl = received_data[1] & 0b01111111

                    if pl == 126:
                        #print("== 126")
                        received_data = self.request.recv(2)
                        payload_length = int.from_bytes(received_data, byteorder="big")

                    elif pl == 127:
                        #print("== 127")
                        received_data = self.request.recv(8)
                        payload_length = int.from_bytes(received_data, byteorder="big")  # 2 -> 10 is 8 bytes
                    else:
                        #print("<126")
                        payload_length = pl

                    # if the masking bit is not 0, the next 4 bytes are the masking bits
                    if masking_bit != 0:
                        #print("mask != 0")
                        received_data = self.request.recv(4)
                        mask = received_data

                    working_load = bytearray()

                    # need to figure out if i need to buffer or not
                    # if i need to buffer, jump into a loop where if the required payload len is > 2048
                    # i grab 2048 and continue buffering,
                    # but if it's less than 2048 i just grab that amount
                    # I can avoid dipping into the wrong bytes this way
                    # The while loop I probably wanna have as the current accumulated len < total len
                    # have an accumulator for the bytes outside the loop
                    if payload_length > 2048:
                        #print("--- payload length exceeds 2048 ---")
                        remaining = payload_length
                        #print("payload_len = " + str(payload_length))
                        #print("remaining = " + str(remaining))
                        #print("working_load = " + str(working_load))
                        #print("--- before loop ---")

                        while len(working_load) < payload_length:
                            # If i need more than 2048 grab 2048 and keep buffering
                            if remaining >= 2048:
                                #print("--- remaining length requires >= 2048 ---")
                                #print("remaining before = " + str(remaining))
                                #print("working_load before = " + str(len(working_load)))
                                received_data = self.request.recv(2048)
                                working_load.extend(received_data)
                                #print("received " + str(len(received_data)) + " bytes")
                                remaining -= len(received_data)
                                #print("remaining now = " + str(remaining))
                                #print("working_load now = " + str(len(working_load)))
                            # Else just grab what I need and add that
                            else:
                                #print("--- remaining length requires < 2048 ---")
                                #print("remaining before = " + str(remaining))
                                #print("working_load before = " + str(len(working_load)))
                                received_data = self.request.recv(remaining)
                                #print("received " + str(len(received_data)) + " bytes")
                                working_load.extend(received_data)
                                remaining -= len(received_data)
                                #print("remaining now = " + str(remaining))
                                #print("working_load now = " + str(len(working_load)))

                    # if buffering isn't needed, just grab payload len bytes from the socket.
                    else:
                        #print("buffering not needed")
                        received_data = self.request.recv(payload_length)
                        working_load.extend(received_data)

                    # AFTER i buffer i can mask and then go from there
                    if masking_bit != 0:
                        print("masking the payload...")
                        for index in range(len(working_load)):  # starts at 0, goes to len - 1
                            # print("index = " + str(index))
                            mask_index = (index + 1) % 4
                            if mask_index == 0:
                                mask_index = 4
                            mask_index -= 1
                            # print("mask index = " + str(mask_index))
                            working_load[index] = working_load[index] ^ mask[mask_index]

                    if fin_bit == 0 or was_zero:
                        #print("continuation frame")
                        working_frame.extend(working_load)

                        if fin_bit == 0:
                            was_zero = True
                        else:
                            was_zero = False
                            #print("generating response")
                            send = util.router.handle_ws_message(working_frame, token)
                            #print("sending")
                            #print("test = " + str(test))
                            for s in test:
                                try:
                                    s.request.sendall(send)
                                except:
                                    continue

                            #print("sent")

                            working_frame = bytearray()

                            # if opcode == 8:
                            #     break
                    else:
                        #print("generating response")
                        send = util.router.handle_ws_message(working_load, token)
                        #print("sending")
                        #print("test = " + str(test))
                        for s in test:
                            try:
                                s.request.sendall(send)
                            except:
                                continue

                        working_load = bytearray()

                        #print("sent")

                        # if opcode == 8:
                        #     break

        else:
            send_me = self.router.route_request(request)
            self.request.sendall(send_me)


def main():
    host = "0.0.0.0"
    port = 8080

    # I was told to change "TCPServer" to "ThreadingTCPServer"
    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))

    server.serve_forever()


if __name__ == "__main__":
    main()
