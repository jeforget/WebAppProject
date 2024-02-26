import array
import json
import random
import socketserver
from util.request import Request
from pymongo import MongoClient
import uuid


class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        received_data = self.request.recv(2048)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)

        # if this is a GET request, handle as get.
        # If it's a POST, handle as post.
        if request.method == "GET":
            send_me = self.handle_get(request)
            self.request.sendall(send_me)
            return
        elif request.method == "POST":
            send_me = self.handle_post(request)
            self.request.sendall(send_me)
        else:
            not_found()

    # ex: HTTP/1.1 404 Not Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 14\r\n\r\nPage not found"

    def handle_get(self, request):

        # check for cookies
        # if this is the first time loading, I need to set the cookie for the first time

        if request.path == "/":

            if not (request.cookies.__contains__("visits")):
                to_send = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: LEN\r\nSet-Cookie: visits=1; Max-Age=3600\r\n\r\n"
                visits = 1
                strvist = "1"
                first = True

            else:
                visits_str = request.cookies.get("visits")

                if visits_str.__contains__(":"):
                    visits_arr = visits_str.split(":")
                    visits_str = visits_arr[0]

                visits_int = int(visits_str)
                visits_int += 1
                strvist = visits_int.__str__()
                tosend = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: LEN\r\nSet-Cookie: visits=1; Max-Age=3600\r\n\r\n"
                to_send = tosend.replace("visits=1", "visits=" + strvist)
                first = False

            with open("public/index.html") as f:
                data = f.read()
                data = data.replace("{{visits}}", strvist)
                e_data = data.encode()
                length = len(e_data)
                ret_send = to_send.replace("LEN", length.__str__())
                send = ret_send.encode()
                return send + e_data

        elif request.path.__contains__(".css"):
            to_send = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/css\r\nContent-Length: LEN\r\n\r\n"
            path = "public/style.css"
            mime = "text/css"
            with open("public/style.css") as f:
                data = f.read()
                e_data = data.encode()
                length = len(e_data)
                ret_send = to_send.replace("LEN", length.__str__())
                send = ret_send.encode()
                return send + e_data

        elif request.path.__contains__("functions.js"):
            to_send = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/javascript\r\nContent-Length: LEN\r\n\r\n"
            with open("public/functions.js") as f:
                data = f.read()
                e_data = data.encode()
                length = len(e_data)
                ret_send = to_send.replace("LEN", length.__str__())
                send = ret_send.encode()
                return send + e_data

        elif request.path.__contains__("webrtc.js"):
            to_send = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/javascript\r\nContent-Length: LEN\r\n\r\n"
            with open("public/webrtc.js") as f:
                data = f.read()
                e_data = data.encode()
                length = len(e_data)
                ret_send = to_send.replace("LEN", length.__str__())
                send = ret_send.encode()
                return send + e_data

        elif request.path.__contains__(".ico"):
            return handle_ico(self, request.path)

        elif request.path.__contains__("public/image"):
            return handle_jpeg(self, request.path)

        elif request.path == "/chat-messages":
            to_send = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: application/json\r\nContent-Length: LEN\r\n\r\n"
            # taken right from the slides
            mongo_client = MongoClient("mongo")
            db = mongo_client["cse312"]
            chat_collection = db["chat"]
            all_data = list(chat_collection.find({}, {"_id": 0}))
            #print(all_data)
            json_data = json.dumps(all_data)
            e_json = json_data.encode()
            j_len = len(e_json)
            send = to_send.replace("LEN", j_len.__str__())
            add_to = send.encode()

            return add_to + e_json


        else:
            return not_found()

    def handle_post(self, request):
        if request.path == "/chat-messages":
            mongo_client = MongoClient("mongo")
            db = mongo_client["cse312"]
            chat_collection = db["chat"]

            # process the body
            body = request.body.decode()
            message_data = json.loads(body)
            # esc_data = escape(message_data)
            mesg = message_data.get("message")
            escp_msg = escape(mesg)
            uid = uuid.uuid4()
            chat_collection.insert_one({"message": escp_msg, "username": "guest", "id": uid.__str__()})
            #print(message_data)
            return "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0\r\n\r\n".encode()
        else:
            print("that can't be right...")
            return


def handle_jpeg(self, path):
    to_send = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: image/jpeg\r\nContent-Length: LEN\r\n\r\n"

    paths = path.split("/")
    file_name = tail(paths)
    n_path = "public/image/" + file_name

    if file_name != "cat.jpg" and file_name != "dog.jpg" and file_name != "eagle.jpg" and file_name != "elephant.jpg" and file_name != "elephant-small.jpg" and file_name != "flamingo.jpg" and file_name != "kitten.jpg":
        return not_found()

    with open(n_path, "rb") as f:
        data = f.read()
        length = len(data)
        ret_send = to_send.replace("LEN", length.__str__())
        e_to_send = ret_send.encode()

        return e_to_send + data


def handle_ico(self, path):
    to_send = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: image/x-icon\r\nContent-Length: LEN\r\n\r\n"

    paths = path.split("/")
    file_name = tail(paths)
    n_path = "public/" + file_name

    with open(n_path, "rb") as f:
        data = f.read()
        length = len(data)
        ret_send = to_send.replace("LEN", length.__str__())
        e_to_send = ret_send.encode()

        return e_to_send + data


# Return the tail of a list
def tail(t_list):
    length = len(t_list)
    return t_list[length - 1]


# Just return an encoded 404 response
def not_found():
    not_found = "HTTP/1.1 404 Not Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 14\r\n\r\nPage not found"
    return not_found.encode()


def escape(string: str):
    string_and = string.replace("&", "&amp")
    string_great = string_and.replace(">", "&gt")
    string_less = string_great.replace("<", "&lt")
    return string_less


def main():
    host = "0.0.0.0"
    port = 8080

    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.TCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))

    server.serve_forever()


if __name__ == "__main__":
    main()
