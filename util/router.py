from util.request import Request
import re
from pymongo import MongoClient
import uuid
import json


# Just return an encoded 404 response
def not_found():
    not_found = "HTTP/1.1 404 Not Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 14\r\n\r\nPage not found"
    return not_found.encode()

def handle_get_chat():
    to_send = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: application/json\r\nContent-Length: LEN\r\n\r\n"
    # taken right from the slides
    mongo_client = MongoClient("mongo")
    db = mongo_client["cse312"]
    chat_collection = db["chat"]
    all_data = list(chat_collection.find({}, {"_id": 0}))
    # print(all_data)
    json_data = json.dumps(all_data)
    e_json = json_data.encode()
    j_len = len(e_json)
    send = to_send.replace("LEN", j_len.__str__())
    add_to = send.encode()

    return add_to + e_json

def escape(string: str):
    string_and = string.replace("&", "&amp")
    string_great = string_and.replace(">", "&gt")
    string_less = string_great.replace("<", "&lt")
    return string_less

def handle_css(request: Request):
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

def handle_html(request: Request):

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

def handle_f_js(request: Request):
    to_send = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/javascript\r\nContent-Length: LEN\r\n\r\n"
    with open("public/functions.js") as f:
        data = f.read()
        e_data = data.encode()
        length = len(e_data)
        ret_send = to_send.replace("LEN", length.__str__())
        send = ret_send.encode()
        return send + e_data

def handle_w_js(request: Request):
    to_send = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/javascript\r\nContent-Length: LEN\r\n\r\n"
    with open("public/webrtc.js") as f:
        data = f.read()
        e_data = data.encode()
        length = len(e_data)
        ret_send = to_send.replace("LEN", length.__str__())
        send = ret_send.encode()
        return send + e_data

# Return the tail of a list
def tail(t_list):
    length = len(t_list)
    return t_list[length - 1]

def handle_img(request: Request):
    path = request.path
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

def handle_ico(request: Request):
    path = request.path
    to_send = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: image/x-icon\r\nContent-Length: LEN\r\n\r\n"

    paths = path.split("/")
    file_name = tail(paths)
    n_path = "public/" + file_name

    with open("public/favicon.ico", "rb") as f:
        data = f.read()
        length = len(data)
        ret_send = to_send.replace("LEN", length.__str__())
        e_to_send = ret_send.encode()

        return e_to_send + data

def handle_post_chat(request: Request):
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
        # print(message_data)
        return "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0\r\n\r\n".encode()
    else:
        print("how did you get here?")


class Router:
    def __init__(self):
        self.get = []
        self.post = []

    def add_route(self, method: str, path: str, func):
        if method == "GET":
            self.get.append((method, path, func))
        elif method == "POST":
            self.post.append((method, path, func))
        else:
            print("you shouldn't be able to get here")

    def route_request(self, req: Request):

        if req.method == "GET":
            for x in self.get:
                if re.match(x[1], req.path):
                    return x[2](req)
        elif req.method == "POST":
            for x in self.post:
                if re.match(x[1], req.path):
                    return x[2](req)
        else:
            return not_found()

if __name__ == '__main__':
    router = Router()
    router.add_route("GET", "^/$", handle_html)
    router.add_route("GET", "^/public/style.css$", handle_css)
    router.add_route("GET", "^/public/functions.js$", handle_f_js)
    router.add_route("GET", "^/public/webrtc.js$", handle_w_js)
    router.add_route("GET", "^/public/image/.", handle_img)
    router.add_route("GET", "^/public/favicon.ico$", handle_ico)
    router.add_route("POST", "^/chat-messages$", handle_post_chat)
    router.add_route("GET", "^/chat-messages$", handle_get_chat)
