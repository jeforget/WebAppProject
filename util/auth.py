import base64
import hashlib

from util.request import Request


def extract_credentials(req: Request):
    # username_reg
    # password_reg
    # username_login
    # password_login

    password = ""
    user = ""
    body = req.body

    b_body = body.decode()
    s_body = b_body.split("&")

    for s in s_body:
        if s.__contains__("username"):
            split_s = s.split("=")
            user = split_s[1]
        if s.__contains__("password"):
            split_s = s.split("=")
            password = split_s[1]

    ret_pass = replace_enc(password)

    return [user, ret_pass]


def replace_enc(pas: str):
    special = ['!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '=']
    pas = pas.replace("%21", "!")
    pas = pas.replace("%40", "@")
    pas = pas.replace("%23", "#")
    pas = pas.replace("%24", "$")
    pas = pas.replace("%5E", "^")
    pas = pas.replace("%5e", "^")
    pas = pas.replace("%26", "&")
    pas = pas.replace("%28", "(")
    pas = pas.replace("%29", ")")
    pas = pas.replace("%3D", "=")
    pas = pas.replace("%3d", "=")
    pas = pas.replace("%2D", "-")
    pas = pas.replace("%2d", "-")
    pas = pas.replace("%5F", "_")
    pas = pas.replace("%5f", "_")
    pas = pas.replace("%25", "%")
    return pas


def validate_password(pas: str):
    # len of < 8
    if len(pas) < 8:
        return False
    # print("has at least len of 8")

    # at least 1 uppercase letter
    if up_or_no(pas):
        return False
    # print("has at least 1 upper")

    # at least 1 lowercase letter
    if low_or_no(pas):
        return False
    # print("has at least 1 lower")

    # at least 1 number
    if num_or_no(pas):
        return False
    # print("has at least 1 num")

    # at least 1 special char
    if spec_or_no(pas):
        return False
    # print("has at least 1 special")

    # no invalid chars
    if alpha_or_no(pas):
        return False
    # print("has no invalid chars")

    return True


# helper function to check for uppercase chars in a string
def up_or_no(pas: str):
    c = 0
    for s in pas:
        if s.isupper():
            c += 1
    if c < 1:
        return True
    else:
        return False


# helper function to check for lowercase chars in a string
def low_or_no(pas: str):
    c = 0
    for s in pas:
        if s.islower():
            c += 1
    if c < 1:
        return True
    else:
        return False


# helper function to check for numeric chars in a string
def num_or_no(pas: str):
    c = 0
    for s in pas:
        if s.isnumeric():
            c += 1
    if c < 1:
        return True
    else:
        return False


# helper function to check for special chars in a string
def spec_or_no(pas: str):
    special = ['!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '=']
    c = 0
    for s in pas:
        for p in special:
            if s == p:
                c += 1
    if c < 1:
        return True
    else:
        return False


# helper function to check for alphanumeric chars in a string
def alpha_or_no(pas: str):
    special = ['!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '=']
    for s in pas:
        c = 0
        if s.isalnum():
            # print(s + " is alpha")
            continue
        else:
            # print(s + " is NOT alpha")
            if special.__contains__(s):
                c = 1
            else:
                return True
    else:
        return False


def test_val_1():
    pwd = "Nova"
    assert not validate_password(pwd)
    pwd_2 = "Ace22"
    assert not validate_password(pwd_2)
    pwd_3 = "Atl@s"
    assert not validate_password(pwd_3)
    pwd_4 = "W1lbuR26!"
    assert validate_password(pwd_4)
    pwd_5 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&()-_=1234567890"
    assert validate_password(pwd_5)


def test_auth_1():
    request = Request(
        b'POST /login HTTP/1.1\r\nHost: foo.example\r\nContent-Type:application/x-www-form-urlencoded\r\nContent-Length: 27\r\n\r\nusername=Nova&password=W1lbUr26!')
    pair = extract_credentials(request)
    assert pair[0] == "Nova"
    assert pair[1] == "W1lbUr26!"


def test_auth_2():
    request = Request(
        b'POST /login HTTP/1.1\r\nHost: foo.example\r\nContent-Type:application/x-www-form-urlencoded\r\nContent-Length: 27\r\n\r\nusername=Nova&password=%21%40%23%24%25%5E%26%28%29%2D%5F%3D')
    special = ['!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '=']
    pair = extract_credentials(request)
    assert pair[0] == "Nova"
    assert pair[1] == "!@#$%^&()-_="


def test_auth_3():
    request = Request(
        b'POST /login HTTP/1.1\r\nHost: foo.example\r\nContent-Type:application/x-www-form-urlencoded\r\nContent-Length: 27\r\n\r\nusername=Nova&password=%21%40%23%24%25%5e%26%28%29%2d%5f%3d')
    pair = extract_credentials(request)
    assert pair[0] == "Nova"
    assert pair[1] == "!@#$%^&()-_="


if __name__ == '__main__':
    test_val_1()
    test_auth_1()
    test_auth_2()
    test_auth_3()

# STUFF FOR HW 4 ------------------------------------------------------------------------------

def compute_accept(key):
    magic_number = "12939rujf2309jr80h283r"  # this is not the real key go check notes
    concat_key = key + magic_number
    sha1_hash = hashlib.sha1(concat_key).decode()
    accept_key = base64.b64encode(sha1_hash).decode()
    return accept_key


def generate_ws_frame(payload):
    payload_length = len(payload)
    frame = bytearray()
    frame.append(0b10000001)
    if payload_length < 126:
        frame.append(payload_length)
        frame.extend(payload)
    elif payload_length < 65536:
        frame.append(126)
        frame.extend(payload_length.to_bytes(2, byteorder="big"))
        frame.extend(payload)
    else:
        frame.append(127)
        frame.extend(payload_length.to_bytes(8, byteorder="big"))
        frame.extend(payload)
    return bytes(frame)

class RecB2:
    def __int__(self):
        self.finbit
        self.opcode
        self.payload_length
        self.payload

def parse_wx_frame(frame):
    output = RecB2()
    output.finbit = (frame[0] & 0b10000000) >> 7 # 0 >> 7 = 0, 128 (256?) >> 7 = 0
    output.opcode = (frame[0] & 0b00001111)

    masking_bit = frame[1] & 0b10000000 # either 0 or 128
    pl = frame[1] & 0b01111111

    if pl == 126:
        output.payload_length = int.from_bytes(frame[2:4], byteorder="big")
        # Moving the frame forward so that we're working with the next chunk
        frame = frame[4:]
    elif pl == 126:
        output.payload_length = int.from_bytes(frame[2:10], byteorder="big") # 2 -> 10 is 8 bytes
        # Moving the frame forward so that we're working with the next chunk
        frame = frame[10:]
    else:
        output.payload_length = pl
        frame = frame[2:]
    # need masking bytes and payload

    # mb can be 0 or some number bc we just &'ed it
    if masking_bit != 0:
        mask = frame[:4]
        frame = frame[4:] # moving it up again

    output.payload = frame

    if masking_bit != 0:
        for index  in range(len(output.payload)): # starts at 0, goes to len - 1
            mask_index = index % 4
            if mask_index == 0:
                mask_index = 4
            mask_index -= 1
            output.payload[index] = output.payload[index] ^ mask[mask_index]




