from util.request import Request
import util.request


# POST /form-path HTTP/1.1/r/nContent-Length: 9937\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundarycriD3u6M0UuPR1ia\r\n\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia\r\nContent-Disposition: form-data; name="commenter"\r\n\r\nJesse\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia\r\nContent-Disposition: form-data; name="upload"; filename="discord.png"\r\nContent-Type: image/png\r\n\r\n<bytes_of_the_file>\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia--\r\n

def parse_multipart(request: Request):
    # The headers should've been safely parsed by util.request
    # If I'm understanding this correctly:
    # My Request object should have all of the headers parsed for me, I just need to extract the boundary from the Content-Type header.
    # The "body" should be the boundaries and everything in between, I just need to parse that split that into parts.

    # Going to start by extracting the boundary from the headers
    c_type = request.headers.get("Content-Type", None)

    # These are always going to have a Content-Type header right? I'm not sure what to have it do if there isn't one...
    # Assuming is dangerous, I'll know where to look if something is wrong...
    if c_type is None:
        print("This shouldn't happen right? Something is very wrong!")

    # c_type should look something like this: "multipart/form-data; boundary=----WebKitFormBoundarycriD3u6M0UuPR1ia"
    # First, split by the ";"
    first_split = c_type.split(';')

    # Then, split by the "="
    boundary_split = first_split[1].split('=')

    # This is the boundary
    boundary = boundary_split[1]

    # Setting up the object
    m_media = Media()

    # Setting the boundary
    m_media.boundary = boundary

    # Next step is to cut up the body into "parts":

    # Replace the "initial" and "final" boundaries with b'', then I can split on the general bound
    first_bound = "--" + boundary + "\r\n"
    final_bound2 = "\r\n--" + boundary + "--"
    final_bound = "\r\n--" + boundary + "--\r\n"
    general_bound = "\r\n--" + boundary + "\r\n"

    body = request.body.replace(first_bound.encode(), b'', 1)
    #print(body)
    body = body.replace(final_bound.encode(), b'')
    #print(body)
    body = body.replace(final_bound2.encode(), b'')
    #print(body)

    body = body.split(general_bound.encode())
    #print(body)

    # Now for every split in body, I can create a part

    for b in body:
        #print("b = " + str(b))
        # Create the part obj
        b_part = Part()

        # First, separate by the \r\n
        split = b.split(b'\r\n\r\n', 1)
        #print("content = " + str(split[1]))
        headers = split[0].split(b'\r\n')
        b_part.content = split[1]

        # Yeah ik this is dumb but I'm gonna just redo my headers code from request
        for h in headers:

            # Headers can safely be decoded now
            h = h.decode()

            # Split by ':'
            head = h.split(':')

            # Insert into headers dict
            b_part.headers[head[0]] = head[1].strip(" ")

        # The Content-Disposition header is gonna look like this:
        # form-data; name="commenter"
        contnent_dip = b_part.headers.get("Content-Disposition", None)
        if contnent_dip is not None:
            name_eq = contnent_dip.split(';')

            # name="commenter"
            name = name_eq[1].split('=')
            b_part.name = name[1].strip('"')

        m_media.parts.append(b_part)

    return m_media

class Media:
    def __init__(self):
        # the value of the boundary from the Content-Type Header as a string
        self.boundary = ""

        # list of parts
        self.parts = []


class Part:
    def __init__(self):
        # A dictionary of all the headers for the part in the same format as a Request object
        self.headers = {}

        # The name from the Content-Disposition header that matches the name of that part in the HTML form as a string
        self.name = ""

        # The content of the part in bytes
        self.content = b''


# Basic test for structure
def test1():
    request = Request(
        b'POST /form-path HTTP/1.1/r/nContent-Length: 9937\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundarycriD3u6M0UuPR1ia\r\n\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia\r\nContent-Disposition: form-data; name="commenter"\r\n\r\nJesse\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia\r\nContent-Disposition: form-data; name="upload"; filename="discord.png"\r\nContent-Type: image/png\r\n\r\n<bytes_of_the_file>\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia--\r\n')
    multi = parse_multipart(request)

    assert multi.parts.__len__() == 2
    assert multi.boundary == "----WebKitFormBoundarycriD3u6M0UuPR1ia"

    assert multi.parts[0].name == "commenter"
    assert 'Content-Disposition' in multi.parts[0].headers
    assert multi.parts[0].content == b'Jesse'
    #print(multi.parts[0].headers)

    assert multi.parts[1].name == "upload"
    assert 'Content-Disposition' in multi.parts[1].headers
    #print(multi.parts[1].content)
    assert multi.parts[1].content == b'<bytes_of_the_file>'
    #print(multi.parts[1].headers)

# Test for \r\n and/or \r\n\r\n inside of the content (can't be corrupting that!)
def test2():
    request = Request(
        b'POST /form-path HTTP/1.1/r/nContent-Length: 9937\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundarycriD3u6M0UuPR1ia\r\n\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia\r\nContent-Disposition: form-data; name="commenter"\r\n\r\nSaurophaganax\r\nmaximus\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia\r\nContent-Disposition: form-data; name="upload"; filename="discord.png"\r\nContent-Type: image/png\r\n\r\n\r\n<bytes_of_the_file>\r\n\r\n\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia--\r\n')
    multi = parse_multipart(request)

    assert multi.parts.__len__() == 2
    assert multi.boundary == "----WebKitFormBoundarycriD3u6M0UuPR1ia"

    assert multi.parts[0].name == "commenter"
    assert 'Content-Disposition' in multi.parts[0].headers
    assert multi.parts[0].content == b'Saurophaganax\r\nmaximus'
    #print(multi.parts[0].headers)

    assert multi.parts[1].name == "upload"
    assert 'Content-Disposition' in multi.parts[1].headers
    assert multi.parts[1].content == b'\r\n<bytes_of_the_file>\r\n\r\n'
    #print(multi.parts[1].headers)

# b'POST /form-path HTTP/1.1\r\nContent-Length: 10000\r\nContent-Type: multipart/form-data; boundary=----thisboundary\r\n\r\n------thisboundary\r\nContent-Disposition: form-data; name="commenter"\r\n\r\nJesse\r\n------thisboundary\r\nContent-Disposition: form-data; name="upload"; filename="cat.png"\r\nContent-Type: image/png\r\n\r\n<bytes_of_file>\r\n------thisboundary--'

def test3():
    request = Request(
        b'POST /form-path HTTP/1.1\r\nContent-Length: 10000\r\nContent-Type: multipart/form-data; boundary=----thisboundary\r\n\r\n------thisboundary\r\nContent-Disposition: form-data; name="commenter"\r\n\r\nJesse\r\n------thisboundary\r\nContent-Disposition: form-data; name="upload"; filename="cat.png"\r\nContent-Type: image/png\r\n\r\n<bytes_of_file>\r\n------thisboundary--'
    )
    multi = parse_multipart(request)

    assert multi.parts.__len__() == 2
    assert multi.boundary == "----thisboundary"

    assert multi.parts[0].name == "commenter"
    assert 'Content-Disposition' in multi.parts[0].headers
    assert multi.parts[0].content == b'Jesse'
    #print(multi.parts[1].headers)

    assert multi.parts[1].name == "upload"
    assert 'Content-Disposition' in multi.parts[1].headers
    #print(multi.parts[1].content)
    assert multi.parts[1].content == b'<bytes_of_file>'
    #print(multi.parts[1].headers)

def test4():
    request = Request(
        b'POST /form-path HTTP/1.1/r/nContent-Length: 9937\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundarycriD3u6M0UuPR1ia\r\n\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia\r\nContent-Disposition: form-data; name="commenter"\r\n\r\nJesse\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia--\r\n')
    multi = parse_multipart(request)

    assert multi.parts.__len__() == 1
    assert multi.boundary == "----WebKitFormBoundarycriD3u6M0UuPR1ia"

    assert multi.parts[0].name == "commenter"
    assert 'Content-Disposition' in multi.parts[0].headers
    assert multi.parts[0].content == b'Jesse'
    #print(multi.parts[0].headers)

if __name__ == "__main__":
    test1()
    test2()
    test3()
    test4()
