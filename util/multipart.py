from util.request import Request


def parse_multipart(request: Request):
    x = 1


class Media:
    def __init__(self):
        # the value of the boundary from the Content-Type Header as a string
        self.boundary = ""

        self.parts = [Part]


class Part:
    def __init__(self):
        # A dictionary of all the headers for the part in the same format as a Request object
        self.headers = {}

        # The name from the Content-Disposition header that matches the name of that part in the HTML form as a string
        self.name = ""

        # The content of the part in bytes
        self.content = b''
