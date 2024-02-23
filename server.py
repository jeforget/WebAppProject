import socketserver
from util.request import Request


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
            not_found()
        else:
            not_found()

    # ex: HTTP/1.1 404 Not Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 14\r\n\r\nPage not found"

    def handle_get(self, request):
        # TODO add the len of the BODY and the THING to the string and then encode it

        if request.path == "/":
            to_send = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: LEN\r\n\r\n"
            with open("public/index.html") as f:
                data = f.read()
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
            mime = "image/x-icon"
            return handle_byte(self, request.path, mime)

        elif request.path.__contains__("public/image"):
            mime = "image/jpeg"
            return handle_byte(self, request.path, mime)

        else:
            return not_found()


def handle_byte(self, path, mimetype):
    to_send = "HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: TYPE\r\nContent-Length: LEN\r\n\r\n"

    if path.__contains__(".ico"):
        paths = path.split("/")
        file_name = tail(paths)
        n_path = "public/" + file_name

        to_send.replace("TYPE", mimetype, 1)
        with open(n_path, "rb") as f:
            data = f.read()
            length = len(data)
            ret_send = to_send.replace("LEN", length.__str__())
            e_to_send = ret_send.encode()

            return e_to_send + data

    paths = path.split("/")
    file_name = tail(paths)
    n_path = "public/image/" + file_name
    print("path = " + n_path)

    to_send.replace("TYPE", mimetype, 1)
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


def main():
    host = "0.0.0.0"
    port = 8080

    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.TCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))

    server.serve_forever()


if __name__ == "__main__":
    main()
