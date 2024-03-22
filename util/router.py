from pymongo import MongoClient
from util.request import Request
import re
import uuid
import json
import util.auth
import bcrypt


#return a 302 Found response that redirects to the home page
def three_o_two():
    return b'HTTP/1.1 302 Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 0\r\nLocation: /public/index.html\r\n\r\n'


# Just return an encoded 404 response
def not_found(req: Request):
    return b'HTTP/1.1 404 Not Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 14\r\n\r\nPage not found'


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
        return not_found(request)

def handle_post_rec(request:Request):
    # format of the body:
    # username_reg=test&password_reg=1234567890
    # parse the body of the request, separating the user and pass
    credent = util.auth.extract_credentials(request)

    # I don't think it says it anywhere in the doc, but I'm assuming usernames can't be empty
    if credent[0] < 1:
        return b'HTTP/1.1 400 Bad Request\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 41\r\n\r\nInvalid Username (must be greater than 0)'

    if not util.auth.validate_password(credent[1]):
        return b'HTTP/1.1 400 Bad Request\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 16\r\n\r\nInvalid Password'

    # if the username and password are valid, generate a salt, append it to the password, and then store the
    # username, salt, and password in the database
    # bcrypt does it all for me!
    password = credent[1]
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)

    esp_username = escape(credent[0])

    # now store the username, salt and hash in the database!
    mongo_client = MongoClient("mongo")
    db = mongo_client["cse312"]
    user_data = db["user_data"]

    # insert the data
    user_data.insert_one({"username": esp_username, "password": hash, "salt": salt})

    # return 302 Found
    return three_o_two()





class Router:
    def __init__(self):
        # self.routes is a list of tuples in this format: (Method, Path, Function)
        self.routes = []

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
        # Simply add the route to the list as a tuple in the form (Method, Path, Function)
        self.routes.append((method, path, func))
        return

    def route_request(self, req: Request):

        # If the list is NOT empty, start looking
        if len(self.routes) > 0:

            # For every tuple in self.routes:
            for x in self.routes:
                # If the method matches, and the re expression matches the path given, return the byte array from the
                # function.

                # The tuple is formatted as (Method, Path, Function), so x[1] is the path and x[2] is the
                # function.

                # I had this as just "if re.match(x[1], req.path):" originally, but re.match seems to
                # return None if it doesn't match, so I set it to != None, and then pyCharm suggested I use "is not"
                # instead.
                #print(req.method + " =? " + x[0])
                #print(req.path + " =? " + x[1])

                if req.method == x[0] and re.match(x[1], req.path) is not None:
                    return x[2](req)
                
            return not_found(req)

        # If the list is empty, or the item cannot be found, return a 404
        else:
            #print("Emtpy!")
            return not_found(req)


# Simple test with GET, and "/"
def test1():
    request = Request(
        b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nPragma: no-cache\r\nCache-Control: no-cache\r\nsec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"\r\nsec-ch-ua-mobile: ?0\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36\r\nsec-ch-ua-platform: "macOS"\r\nAccept: */*\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: cors\r\nSec-Fetch-Dest: empty\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: Pycharm-3b3d647e=9c644a39-df20-4fb8-a4dd-e1dcdfd170c1; visits=6\r\n\r\nHelloWorld')
    r = Router()
    r.add_all_routes()
    r.add_route("GET", "^/public/style.css$", handle_css)
    route = r.route_request(request)
    #print(route)


# Simple test with GET and an image
def test2():
    request = Request(
        b'GET /public/image/eagle.jpg HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nsec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"\r\nsec-ch-ua-mobile: ?0\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36\r\nsec-ch-ua-platform: "macOS"\r\nAccept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: no-cors\r\nSec-Fetch-Dest: image\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: Pycharm-3b3d647e=9c644a39-df20-4fb8-a4dd-e1dcdfd170c1; visits=5\r\n\r\n'
    )
    r = Router()
    r.add_all_routes()
    route = r.route_request(request)
    #print(route)


# Simple test with POST and a chat message
def test3():
    request = Request(
        b'POST /chat-messages HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 18\r\nsec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"\r\nsec-ch-ua-platform: "macOS"\r\nsec-ch-ua-mobile: ?0\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36\r\nContent-Type: text/plain;charset=UTF-8\r\nAccept: */*\r\nOrigin: http://localhost:8080\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: cors\r\nSec-Fetch-Dest: empty\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: Pycharm-3b3d647e=9c644a39-df20-4fb8-a4dd-e1dcdfd170c1; visits=5\r\n\r\n{"message":"test"}')
    r = Router()
    r.add_all_routes()
    route = r.route_request(request)
    #print(route)

# Simple test with DELETE (something other than GET or POST)
def test4():
    request = Request(
        b'DELETE / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 18\r\nsec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"\r\nsec-ch-ua-platform: "macOS"\r\nsec-ch-ua-mobile: ?0\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36\r\nContent-Type: text/plain;charset=UTF-8\r\nAccept: */*\r\nOrigin: http://localhost:8080\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: cors\r\nSec-Fetch-Dest: empty\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: Pycharm-3b3d647e=9c644a39-df20-4fb8-a4dd-e1dcdfd170c1; visits=5\r\n\r\n{"message":"test"}')
    r = Router()
    r.add_all_routes()
    route = r.route_request(request)
    #print(route)

# Simple test for if the path does not exist (return 404)
def test5():
    request = Request(
        b'DELETE / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 18\r\nsec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"\r\nsec-ch-ua-platform: "macOS"\r\nsec-ch-ua-mobile: ?0\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36\r\nContent-Type: text/plain;charset=UTF-8\r\nAccept: */*\r\nOrigin: http://localhost:8080\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: cors\r\nSec-Fetch-Dest: empty\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: Pycharm-3b3d647e=9c644a39-df20-4fb8-a4dd-e1dcdfd170c1; visits=5\r\n\r\n{"message":"test"}')
    r = Router()
    r.add_all_routes()
    #print(route)


if __name__ == "__main__":
    test1()
    test2()
    test4()
    test5()
