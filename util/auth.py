from util.request import Request


def extract_credentials(req: Request):
    print("test output")
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

    print("pass = " + ret_pass)
    print("user = " + user)

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
    print("has at least len of 8")

    # at least 1 uppercase letter
    if up_or_no(pas):
        return False
    print("has at least 1 upper")

    # at least 1 lowercase letter
    if low_or_no(pas):
        return False
    print("has at least 1 lower")

    # at least 1 number
    if num_or_no(pas):
        return False
    print("has at least 1 num")

    # at least 1 special char
    if spec_or_no(pas):
        return False
    print("has at least 1 special")

    # no invalid chars
    if alpha_or_no(pas):
        return False
    print("has no invalid chars")

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
            print(s + " is alpha")
        else:
            print(s + " is NOT alpha")
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
