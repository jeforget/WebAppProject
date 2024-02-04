class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables

        self.body = b""
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
        self.cookies = {}

        req = request.decode()
        # start by splitting the request at \r\n\r\n
        splitby1 = req.split("\r\n\r\n", 1)
        print("First split = " + str(splitby1))

        # split the first half by \r\n
        splitby2 = splitby1[0].split("\r\n")
        print("splitby2 = " + str(splitby2))

        # take the request line and split by " ", then place the method, body, and ver in respective vars.
        req_line = splitby2[0].split(" ")
        self.method = req_line[0]
        self.http_version = req_line[2]
        self.path = req_line[1]

        i = 1
        while i < len(splitby2):
            head = splitby2[i].split(":",1)
            print("head = " + str(head))
            key = head[0].strip()
            print("key = " + str(key))
            val = head[1].strip()
            print("val = " + str(val))
            self.headers[key] = val
            i += 1

        if splitby1[1] != '':
            self.body = splitby1[1].encode()




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
    request = Request(b'GET / HTTP/1.1\r\nHost: cse312.com\r\nConnection: keep-alive\r\nAccept-Language: en-US,en\r\n\r\n')
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "cse312.com"  # note: The leading space in the header value must be removed
    assert request.body == b""  # There is no body for this request.
    # When parsing POST requests, the body must be in bytes, not str

def test3():
    request = Request(b'POST /test HTTP/1.1\r\nHost: foo.example\r\nContent-Type:application/x-www-form-urlencoded\r\nContent-Length: 27\r\n\r\nfield1=value1&field2=value2')
    assert request.method == "POST"
    assert "Host" in request.headers
    assert request.headers["Host"] == "foo.example"  # note: The leading space in the header value must be removed
    assert request.headers["Content-Type"] == "application/x-www-form-urlencoded" # Test for no space
    assert request.body == b"field1=value1&field2=value2"  # There is a body for this request.
    # When parsing POST requests, the body must be in bytes, not str


if __name__ == '__main__':
    test1()
    test2()
    test3()
