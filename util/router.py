from pymongo import MongoClient
from util.request import Request
import re
import uuid
import json


# Just return an encoded 404 response
def not_found(req: Request):
    not_f = "HTTP/1.1 404 Not Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 14\r\n\r\nPage not found"
    return not_f.encode()


def handle_get_chat(req: Request):
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
        return not_found(request)

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
        return "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0\r\n\r\n".encode()


class Router:
    def __init__(self):
        # self.get is a list of tuples in this format: (Method, Path, func)
        self.get = []

        # self.post is a list of tuples in this format: (Method, Path, func)
        self.post = []

# A function that adds all of my routes for me
    def add_all_routes(self):
        self.add_route("GET", "^/public/style.css$", handle_css)
        self.add_route("GET", "^/public/functions.js$", handle_f_js)
        self.add_route("GET", "^/public/webrtc.js$", handle_w_js)
        self.add_route("GET", "^/public/image/.", handle_img)
        self.add_route("GET", "^/public/favicon.ico$", handle_ico)
        self.add_route("GET", "^/chat-messages$", handle_get_chat)
        self.add_route("POST", "^/chat-messages$", handle_post_chat)
        self.add_route("GET", "^/$", handle_html)

    def add_route(self, method: str, path: str, func):
        # If the method is get, append a tuple of (method, path, func) to the self.get list
        if method == "GET":
            self.get.append((method, path, func))
        #  If the method is post, append a tuple of (method, path, func) to the self.get list
        elif method == "POST":
            self.post.append((method, path, func))
        # This router only handles get and post, if the method is neither of them, just return without doing anything
        else:
            return

    def route_request(self, req: Request):

        # If the method of the request is get, look into self.get
        if req.method == "GET":
            # For every tuple in self.get:
            for x in self.get:
                # If the re expression matches the path given, return the byte array from the function
                if re.match(x[1], req.path) is not None:
                    return x[2](req)
            # If you've gotten this far, that means it's not in there so just return an encoded 404
            return not_found(req)
        # If the method of the request is post, look into self.post
        elif req.method == "POST":
            # For every tuple in self.post:
            for x in self.post:
                # If the re expression matches the path given, return the byte array from the function
                if re.match(x[1], req.path) is not None:
                    return x[2](req)
            # If you've gotten this far, that means it's not in there so just return an encoded 404
            return not_found(req)
        # This router only handles post and get, anything else is just a 404
        else:
            return not_found(req)

# Simple test with GET, and "/"
def test1():
    request = Request(
        b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nPragma: no-cache\r\nCache-Control: no-cache\r\nsec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"\r\nsec-ch-ua-mobile: ?0\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36\r\nsec-ch-ua-platform: "macOS"\r\nAccept: */*\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: cors\r\nSec-Fetch-Dest: empty\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: Pycharm-3b3d647e=9c644a39-df20-4fb8-a4dd-e1dcdfd170c1; visits=6\r\n\r\nHelloWorld')
    r = Router()
    r.add_all_routes()
    route = r.route_request(request)
    print(route)

# Simple test with GET and an image
def test2():
    request = Request(
        b'GET /public/image/eagle.jpg HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nsec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"\r\nsec-ch-ua-mobile: ?0\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36\r\nsec-ch-ua-platform: "macOS"\r\nAccept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: no-cors\r\nSec-Fetch-Dest: image\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: Pycharm-3b3d647e=9c644a39-df20-4fb8-a4dd-e1dcdfd170c1; visits=5\r\n\r\n'
    )
    r = Router()
    r.add_all_routes()
    route = r.route_request(request)
    print(route)

# Simple test with POST and a chat message
def test3():
    request = Request(
        b'POST /chat-messages HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 18\r\nsec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"\r\nsec-ch-ua-platform: "macOS"\r\nsec-ch-ua-mobile: ?0\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36\r\nContent-Type: text/plain;charset=UTF-8\r\nAccept: */*\r\nOrigin: http://localhost:8080\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: cors\r\nSec-Fetch-Dest: empty\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: Pycharm-3b3d647e=9c644a39-df20-4fb8-a4dd-e1dcdfd170c1; visits=5\r\n\r\n{"message":"test"}')
    r = Router()
    r.add_all_routes()
    route = r.route_request(request)
    print(route)


if __name__ == "__main__":
    test1()
    test2()
    test3()
