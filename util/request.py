class Request:

    def __init__(self, request: bytes):


        self.body = b""
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
        self.cookies = {}

        req = request.decode()
        # start by splitting the request at \r\n\r\n
        splitby1 = req.split("\r\n\r\n", 1)
        # print("First split = " + str(splitby1))

        # split the first half by \r\n
        splitby2 = splitby1[0].split("\r\n")
        # print("splitby2 = " + str(splitby2))

        # take the request line and split by " ", then place the method, body, and ver in respective vars.
        req_line = splitby2[0].split(" ")
        self.method = req_line[0]
        self.http_version = req_line[2]
        self.path = req_line[1]

        i = 1
        while i < len(splitby2):
            head = splitby2[i].split(":", 1)
            # print("head = " + str(head))
            key = head[0].strip()
            # print("key = " + str(key))
            val = head[1].strip()
            # print("val = " + str(val))
            self.headers[key] = val
            i += 1

        if splitby1[1] != '':
            self.body = splitby1[1].encode()

        handle_cookies(self)


def handle_cookies(self):
    # go through the headers and grab the cookies

    cookie = self.headers.get("Cookie", "no")

    if cookie != "no":
        if ";" in cookie:
            cook = cookie.split(";")
            for co in cook:
                split_by_eq(self, co)
        else:
            split_by_eq(self, cookie)


def split_by_eq(self, cookie):
    split_cookie = cookie.split("=")
    self.cookies[split_cookie[0].strip()] = split_cookie[1].strip()


def test1():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n')
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
    assert request.body == b""  # There is no body for this request.
    # When parsing POST requests, the body must be in bytes, not str

    # This is the start of a simple way (ie. no external libraries) to test your code.
    # It's recommended that you complete this test and add others, including at least one
    # test using a POST request. Also, ensure that the types of all values are correct


def test2():
    request = Request(
        b'GET / HTTP/1.1\r\nHost: cse312.com\r\nConnection: keep-alive\r\nAccept-Language: en-US,en\r\n\r\n')
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "cse312.com"  # note: The leading space in the header value must be removed
    assert request.body == b""  # There is no body for this request.
    # When parsing POST requests, the body must be in bytes, not str


def test3():
    request = Request(
        b'POST /test HTTP/1.1\r\nHost: foo.example\r\nContent-Type:application/x-www-form-urlencoded\r\nContent-Length: 27\r\n\r\nfield1=value1&field2=value2')
    assert request.method == "POST"
    assert "Host" in request.headers
    assert request.headers["Host"] == "foo.example"  # note: The leading space in the header value must be removed
    assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"  # Test for no space
    assert request.body == b"field1=value1&field2=value2"  # There is a body for this request.
    # When parsing POST requests, the body must be in bytes, not str

def test4():
    request = Request(
        b'POST /test HTTP/1.1\r\nHost: foo.example\r\nContent-Type:application/x-www-form-urlencoded\r\nCookie: id=X6kAwpgW29M\r\n\r\nfield1=value1&field2=value2')
    assert request.method == "POST"
    assert "Host" in request.headers
    assert "id" in request.cookies
    assert request.body == b"field1=value1&field2=value2"  # There is a body for this request.
    # When parsing POST requests, the body must be in bytes, not str

def test5():
    request = Request(
        b'POST /register HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 41\r\nCache-Control: max-age=0\r\nsec-ch-ua: "Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "macOS"\r\nUpgrade-Insecure-Requests: 1\r\nOrigin: http://localhost:8080\r\nContent-Type: application/x-www-form-urlencoded\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: Pycharm-3b3d647e=9c644a39-df20-4fb8-a4dd-e1dcdfd170c1; session=eyJ1c2VybmFtZSI6bnVsbH0.ZfyNXw.LWoVYAQLOKe8vSy0uWFTzJYLWg4; visits=1\r\n\r\nusername_reg=test&password_reg=1234567890')
    assert request.method == "POST"
    assert "Host" in request.headers
    assert "id" in request.cookies
    assert request.cookies["id"] == "X6kAwpgW29M"
    #print(request.cookies)
    assert "visits" in request.cookies
    assert request.body == b"username_reg=test&password_reg=1234567890"  # There is a body for this request.
    # When parsing POST requests, the body must be in bytes, not str


if __name__ == '__main__':
    test1()
    test2()
    test3()
    test4()
    test5()