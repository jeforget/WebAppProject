from util.request import Request


class Router:
    def __init__(self):
        self.route = str

    def add_route(self, method: str, path: str, func):
        self.route = self.not_found()

    def route_request(self, req: Request):

        return

    # Just return an encoded 404 response
    def not_found(self):
        not_found = "HTTP/1.1 404 Not Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 14\r\n\r\nPage not found"
        return not_found.encode()


if __name__ == "__main__":
    pass
