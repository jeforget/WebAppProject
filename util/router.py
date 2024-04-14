from pymongo import MongoClient
from util.request import Request
import util.multipart
import re
import uuid
import json
import util.auth
import bcrypt
import string
import secrets
from hashlib import sha256


# This is pretty much doing exactly what handle_post_chat is doing.
# Should I have made a single function that I could call for both? Yes. However, I did not.
def send_img_to_db(request: Request, html: str):
    # Connect to the db
    mongo_client = MongoClient("mongo")
    db = mongo_client["cse312"]
    chat_collection = db["chat"]

    uid = uuid.uuid4()

    token = request.cookies.get('auth', "none")

    if token != "none":
        user_data = db["user_data"]

        n_hash = sha256(token.encode()).digest()

        data = list(user_data.find({"auth": n_hash}))
        # print("DATA = " + str(data))
        if data.__len__() > 0:
            user_stuff = data[0]
            username = user_stuff['username']
            # print("POSTED AS: " + username)

            # since the user is authenticated, check for x_token next
            x_token = user_stuff['token']

            # I'll get beck to this later
            # tok = message_data.get("token", "NONE")

            # print("b = " + str(tok))
            # if x_token != tok:
            # 403
            #    return "HTTP/1.1 403 Forbidden\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0\r\n\r\n".encode()

            chat_collection.insert_one({"message": html, "username": username, "id": uid.__str__()})
            return "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0\r\n\r\n".encode()

    chat_collection.insert_one({"message": html, "username": "guest", "id": uid.__str__()})
    # print("POSTED AS: guest")
    return "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0\r\n\r\n".encode()


def handle_post_image(request: Request):
    # Start by giving this request to multipart for parsing
    multi_request = util.multipart.parse_multipart(request)

    # Bytes of the image
    image = b''
    file_type = ""
    for part in multi_request.parts:
        if part.name == "upload":
            image = part.content
            #print("content dip = " + part.headers.get("Content-Disposition", ""))
            if part.headers.get("Content-Disposition", "").__contains__("jpg"):
                #print("contains jpg")
                file_type = "jpg"
            if part.headers.get("Content-Disposition", "").__contains__("mp4"):
                #print("conatins mp4")
                file_type = "mp4"

    # Unique id for this image
    uid = str(uuid.uuid4())
    # print("The unique name for this image is " + uid)

    # Save this image to disk

    with open("public/image/" + uid, "wb") as output_file:
        output_file.write(image)

    # Save <img src=”/public/images/user_upload1” alt=”an image of something” class=”my_image/> to the db as a chat message same as usual
    #print("filetype = " + file_type)
    if file_type == "jpg":
        html = '<img src="/public/image/NAME" alt="This should not be seen..." class="my_image"/>'
        html_send = html.replace("NAME", uid)
    elif file_type == "mp4":
        html = '<video width="400" controls autoplay muted><source src="/public/image/NAME" type="video/mp4"></video>'
        html_send = html.replace("NAME", uid)
    else:
        html_send = 'file type not supported!'

    send_img_to_db(request, html_send)

    return three_o_two()


def handle_logout(request: Request):
    mongo_client = MongoClient("mongo")
    db = mongo_client["cse312"]

    # hoho now we can grab the cookie (I just finished setting up the auth token)
    # print("COOKIES = " + str(request.cookies))
    token = request.cookies.get('auth', "none")
    # print("TOKEN = " + str(token))

    if token != "none":
        user_data = db["user_data"]

        n_hash = sha256(token.encode()).digest()

        data = list(user_data.find({"auth": n_hash}))
        # print("DATA = " + str(data))
        if data.__len__() > 0:
            user_stuff = data[0]
            username = user_stuff['username']
            pwd = user_stuff['password']
            salt = user_stuff['salt']

            user_data.delete_many({"username": username})

            user_data.insert_one({"username": username, "password": pwd, "salt": salt, "auth": b'', "token": ""})

            return three_o_two()

    return "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0\r\n\r\n".encode()


# return a 302 Found response that redirects to the home page
def three_o_two():
    return b'HTTP/1.1 302 Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 0\r\nLocation: /\r\n\r\n'


# Just return an encoded 404 response
def not_found(req: Request):
    return b'HTTP/1.1 404 Not Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 14\r\n\r\nPage not found'


def handle_delete_chat(request: Request):
    mongo_client = MongoClient("mongo")
    db = mongo_client["cse312"]
    chat_collection = db["chat"]

    # hoho now we can grab the cookie (I just finished setting up the auth token)
    # print("COOKIES = " + str(request.cookies))
    token = request.cookies.get('auth', "none")
    # print("TOKEN = " + str(token))

    if token != "none":
        user_data = db["user_data"]

        n_hash = sha256(token.encode()).digest()

        data = list(user_data.find({"auth": n_hash}))
        # print("DATA = " + str(data))
        if data.__len__() > 0:
            user_stuff = data[0]
            username = user_stuff['username']

            # /chat-messages/bd0eda8a-75b0-454a-b531-e8530a844c4f
            # /chat-messages/bd0eda8a-75b0-454a-b531-e8530a844c4f
            # /chat-messages/1de9f220-fb64-4df5-a9e1-d4365a63961c

            path = request.path.split('/')
            msg_id = path[2]

            mesg = list(chat_collection.find({"id": msg_id}))
            q_msg = mesg[0]

            if q_msg["username"] == username:
                chat_collection.delete_one({"id": msg_id})
                return "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0\r\n\r\n".encode()

    return "HTTP/1.1 403 Forbidden\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0\r\n\r\n".encode()


def handle_get_chat(req: Request):
    to_send = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: application/json\r\nContent-Length: LEN\r\n\r\n"
    # taken right from the slides
    mongo_client = MongoClient("mongo")
    db = mongo_client["cse312"]
    chat_collection = db["chat"]
    # , {"_id": 0}
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

        # Logout:\n<form action="/logout" method="post" enctype="application/x-www-form-urlencoded">\n<input type="submit" value="Post">\n</form>

        # if the auth token cookie matches the auth token in the db, have logout appear

        token = request.cookies.get('auth', "none")

        mongo_client = MongoClient("mongo")
        db = mongo_client["cse312"]

        if token != "none":
            user_data = db["user_data"]

            n_hash = sha256(token.encode()).digest()

            u_data = list(user_data.find({"auth": n_hash}))

            if u_data.__len__() > 0:
                data = data.replace("{{logout}}",
                                    'Logout:\n<form action="/logout" method="post" enctype="application/x-www-form-urlencoded">\n<input type="submit" value="Post">\n</form>')

                # if this is an authenticated user, issue them an xsrf token, save it to the database, then embed it into the html
                chars = string.ascii_letters + string.digits + '!@#$%^&*()'
                len = 20
                x_token = ''.join(secrets.choice(chars) for i in range(len))

                # insert into html
                data = data.replace("{{token}}", x_token)

                # insert into db
                username = u_data[0]["username"]
                hashword = u_data[0]["password"]
                salt = u_data[0]["salt"]
                hash_token = u_data[0]["auth"]
                user_data.delete_many({"username": username})
                user_data.insert_one({"username": username, "password": hashword, "salt": salt, "auth": hash_token,
                                      "token": x_token})

            else:
                data = data.replace("{{logout}}", "")
        # else, have it not do that
        else:
            data = data.replace("{{logout}}", "")

        e_data = data.encode()
        length = e_data.__len__()
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

    # Since I don't have any "/"s in my file names, this should be safe to do
    paths = path.split("/")
    file_name = tail(paths)
    # On the off chance that splitting on "/" doesn't protect me, I'm also replacing all "/"s.
    n_path = "public/image/" + file_name .replace("/", "")


    #print("n_path = " + n_path)

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

        # hoho now we can grab the cookie (I just finished setting up the auth token, pretty excited)
        # print("COOKIES = " + str(request.cookies))
        token = request.cookies.get('auth', "none")
        # print("TOKEN = " + str(token))

        if token != "none":
            user_data = db["user_data"]

            n_hash = sha256(token.encode()).digest()

            data = list(user_data.find({"auth": n_hash}))
            # print("DATA = " + str(data))
            if data.__len__() > 0:
                user_stuff = data[0]
                username = user_stuff['username']
                # print("POSTED AS: " + username)

                # since the user is authenticated, check for x_token next
                x_token = user_stuff['token']

                # body = {"message":"test","token":"@VJCeuau!6S*h&5AxzHm"}

                tok = message_data.get("token", "NONE")

                # print("b = " + str(tok))
                if x_token != tok:
                    # 403
                    return "HTTP/1.1 403 Forbidden\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0\r\n\r\n".encode()

                chat_collection.insert_one({"message": escp_msg, "username": username, "id": uid.__str__()})
                return "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0\r\n\r\n".encode()

        chat_collection.insert_one({"message": escp_msg, "username": "guest", "id": uid.__str__()})
        # print("POSTED AS: guest")
        return "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0\r\n\r\n".encode()
    else:
        return not_found(request)


def handle_post_rec(request: Request):
    # format of the body:
    # username_reg=test&password_reg=1234567890
    # parse the body of the request, separating the user and pass
    credent = util.auth.extract_credentials(request)

    # I don't think it says it anywhere in the doc, but I'm assuming usernames can't be empty
    if credent[0].__len__() < 1:
        return three_o_two()

    if not util.auth.validate_password(credent[1]):
        return three_o_two()

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
    user_data.insert_one({"username": esp_username, "password": hash, "salt": salt, "auth": b'', "token": ""})

    # return 302 Found
    return three_o_two()


def handle_login(request: Request):
    # grab username and password from the request
    credent = util.auth.extract_credentials(request)

    # grab the login info from the database
    mongo_client = MongoClient("mongo")
    db = mongo_client["cse312"]
    user_data = db["user_data"]

    data = list(user_data.find({"username": credent[0]}))
    # returns what looks like a list of dicts
    # [{'_id': ObjectId('65fdf69476cb9986210ddabc'), 'username': 'Justin', 'password': b'$2b$12$FBHi4QbwAW4T2NNqrHJmoediED8iGb8FfCao1dl6MVH5FWJfJiCPq', 'salt': b'$2b$12$FBHi4QbwAW4T2NNqrHJmoe'}]

    # if the list is not empty:
    if data.__len__() > 0:
        # print("data = " + str(data[0]))
        # there should only be 1 user with this name...
        entry_one = data[0]
        username = entry_one['username']
        # remember, the hash is a byte array, do NOT treat like a string!
        hashword = entry_one['password']
        # salt is also stored as bytes!
        salt = entry_one['salt']
        x_token = entry_one['token']

        # "unhash" and make sure the passwords match, if they do, create an auth token and overwrite the old auth token

        # encoding user password
        input_pass = credent[1].encode('utf-8')

        # checking password
        result = bcrypt.checkpw(input_pass, hashword)

        if result:
            # make sure to set this new auth token in a response, and destroy the old one
            # remember to set the Httponly directive!

            # auth tokens are just random right?
            len = 20
            chars = string.ascii_letters + string.digits + '!@#$%^&*()'
            token = ''.join(secrets.choice(chars) for i in range(len))
            cookie = 'Set-Cookie: auth=' + token + ';Max-Age=3600; HttpOnly'

            # Hash the auth token for storage
            hash_token = sha256(token.encode()).digest()

            # try a different way...
            user_data.delete_many({"username": username})

            user_data.insert_one(
                {"username": username, "password": hashword, "salt": salt, "auth": hash_token, "token": x_token})

            # setting up the response
            response = 'HTTP/1.1 302 Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 0\r\nLocation: /\r\nCOOKIE\r\n\r\n'
            return_response = response.replace('COOKIE', cookie)
            # print("LOGIN SUCCESSFUL")
            return return_response.encode()

    # if this user doesn't exist, from what I read in the handout I don't really do anything.
    # print("LOGIN FAILED")
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
        self.add_route("POST", "^/register$", handle_post_rec)
        self.add_route("POST", "^/login$", handle_login)
        self.add_route("DELETE", "^/chat-messages", handle_delete_chat)
        self.add_route("POST", "^/logout$", handle_logout)
        self.add_route("POST", "^/form-path$", handle_post_image)

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
                # print(req.method + " =? " + x[0])
                # print(req.path + " =? " + x[1])

                if req.method == x[0] and re.match(x[1], req.path) is not None:
                    return x[2](req)

            return not_found(req)

        # If the list is empty, or the item cannot be found, return a 404
        else:
            # print("Emtpy!")
            return not_found(req)


# Simple test with GET, and "/"
def test1():
    request = Request(
        b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nPragma: no-cache\r\nCache-Control: no-cache\r\nsec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"\r\nsec-ch-ua-mobile: ?0\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36\r\nsec-ch-ua-platform: "macOS"\r\nAccept: */*\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: cors\r\nSec-Fetch-Dest: empty\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: Pycharm-3b3d647e=9c644a39-df20-4fb8-a4dd-e1dcdfd170c1; visits=6\r\n\r\nHelloWorld')
    r = Router()
    r.add_all_routes()
    r.add_route("GET", "^/public/style.css$", handle_css)
    route = r.route_request(request)
    # print(route)


# Simple test with GET and an image
def test2():
    request = Request(
        b'GET /public/image/eagle.jpg HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nsec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"\r\nsec-ch-ua-mobile: ?0\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36\r\nsec-ch-ua-platform: "macOS"\r\nAccept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: no-cors\r\nSec-Fetch-Dest: image\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: Pycharm-3b3d647e=9c644a39-df20-4fb8-a4dd-e1dcdfd170c1; visits=5\r\n\r\n'
    )
    r = Router()
    r.add_all_routes()
    route = r.route_request(request)
    # print(route)


# Simple test with POST and a chat message
def test3():
    request = Request(
        b'POST /chat-messages HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 18\r\nsec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"\r\nsec-ch-ua-platform: "macOS"\r\nsec-ch-ua-mobile: ?0\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36\r\nContent-Type: text/plain;charset=UTF-8\r\nAccept: */*\r\nOrigin: http://localhost:8080\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: cors\r\nSec-Fetch-Dest: empty\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: Pycharm-3b3d647e=9c644a39-df20-4fb8-a4dd-e1dcdfd170c1; visits=5\r\n\r\n{"message":"test"}')
    r = Router()
    r.add_all_routes()
    route = r.route_request(request)
    # print(route)


# Simple test with DELETE (something other than GET or POST)
def test4():
    request = Request(
        b'DELETE / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 18\r\nsec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"\r\nsec-ch-ua-platform: "macOS"\r\nsec-ch-ua-mobile: ?0\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36\r\nContent-Type: text/plain;charset=UTF-8\r\nAccept: */*\r\nOrigin: http://localhost:8080\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: cors\r\nSec-Fetch-Dest: empty\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: Pycharm-3b3d647e=9c644a39-df20-4fb8-a4dd-e1dcdfd170c1; visits=5\r\n\r\n{"message":"test"}')
    r = Router()
    r.add_all_routes()
    route = r.route_request(request)
    # print(route)


# Simple test for if the path does not exist (return 404)
def test5():
    request = Request(
        b'DELETE / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 18\r\nsec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"\r\nsec-ch-ua-platform: "macOS"\r\nsec-ch-ua-mobile: ?0\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36\r\nContent-Type: text/plain;charset=UTF-8\r\nAccept: */*\r\nOrigin: http://localhost:8080\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: cors\r\nSec-Fetch-Dest: empty\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: Pycharm-3b3d647e=9c644a39-df20-4fb8-a4dd-e1dcdfd170c1; visits=5\r\n\r\n{"message":"test"}')
    r = Router()
    r.add_all_routes()
    # print(route)


if __name__ == "__main__":
    test1()
    test2()
    test4()
    test5()

    # /chat-messages/bd0eda8a-75b0-454a-b531-e8530a844c4f
    # /chat-messages/bd0eda8a-75b0-454a-b531-e8530a844c4f
    # /chat-messages/1de9f220-fb64-4df5-a9e1-d4365a63961c
