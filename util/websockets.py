import base64
import hashlib

def compute_accept(key):
    magic_number = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    concat_key = (key + magic_number).encode()
    sha1_hash = hashlib.sha1(concat_key).digest()
    accept_key = base64.b64encode(sha1_hash).decode()
    return accept_key


def parse_ws_frame(frame):
    output = Frame()
    output.fin_bit = (frame[0] & 0b10000000) >> 7  # 0 >> 7 = 0, 128 (256?) >> 7 = 1
    output.opcode = (frame[0] & 0b00001111)

    masking_bit = frame[1] & 0b10000000  # either 0 or 128
    pl = frame[1] & 0b01111111

    if pl == 126:
        output.payload_length = int.from_bytes(frame[2:4], byteorder="big")
        # Moving the frame forward so that we're working with the next chunk
        frame = frame[4:]
    elif pl == 127:
        output.payload_length = int.from_bytes(frame[2:10], byteorder="big")  # 2 -> 10 is 8 bytes
        # Moving the frame forward so that we're working with the next chunk
        frame = frame[10:]
    else:
        output.payload_length = pl
        frame = frame[2:]
    # need masking bytes and payload

    # mb can be 0 or some number bc we just &'ed it
    if masking_bit != 0:
        mask = frame[:4]
        frame = frame[4:]  # moving it up again

    payload = bytearray(frame)  # I think this is my problem

    if masking_bit != 0:
        for index in range(len(payload)):  # starts at 0, goes to len - 1
            #print("index = " + str(index))
            mask_index = (index + 1) % 4
            if mask_index == 0:
                mask_index = 4
            mask_index -= 1
            #print("mask index = " + str(mask_index))
            payload[index] = payload[index] ^ mask[mask_index]

    output.payload = bytes(payload)

    return output


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


# When you do the handshake is the only time you can authenticate; after that do the while loop
# then call receive

class Frame:
    def __init__(self):
        # An int with the value of the fin bit (Either 1 or 0)
        self.fin_bit = int

        # Mask = 15 (not the same as the mask bit)
        # 1000 (8) = close <- if opcode == 8, break
        # 0000 continuation <- don't have to check for this, just look at fin bit. Check for 1000
        # An int with the value of the opcode (eg. if the op code is bx1000, this field stores 8 as an int)
        self.opcode = int

        # Read 7 bit length
        # If 126, read next 16 bits as length
        # If 127, read the next 64 bits as length
        # Else, read the value itself as the lengh.
        # The payload length as an int. Your function must handle all 3 payload length modes
        self.payload_length = int

        # The unmasked bytes of the payload
        self.payload = bytes

        # mask bit is always 0 when sending, always 1 when reciveing


def test1():
    byt = b'jfn948hpf9845gp984h5gnvh45ngm984h5g0984h5go4hfp983h3bf8h3-fp983f3i01234567898y9hfpu4owgfhobubfpq3u948fv1y3pfy8n13948hpv3g4fcgh47fp34hfp348yfno7y3h40jv2ny457t28hmv24578tvn2m4578ntv'
    print(byt)
    byt2 = b'987654321'

    byts = b'1234567890'

    rand_str = "Allosaurus-fragilis-Saurophaganax-maxiumus"

    acc = compute_accept(rand_str)

    print(acc)

    frame = bytearray()
    frame.append(0b10000000)
    frame.append(0b00000010)
    frame.append(0b10110100)
    frame.append(0b01100110)

    parsed = parse_ws_frame(frame)

    print(parsed.payload)
    print(parsed.fin_bit)
    print(parsed.payload_length)
    print(parsed.opcode)

    # 1 in binary is 00000001 and 128 is 10000000, so 1 & 128 = 00000000
    # for i in range(len(byt)):
    #     if i > 7:
    #         mask = i % 4 + 1
    #         print("use mask " + str(mask))
    #     else:
    #         print("no mask")


def test2():
    frame = bytearray()
    frame.append(0b10000000)
    frame.append(0b00000010)
    frame.append(0b10110100)
    frame.append(0b01100110)

    parsed = parse_ws_frame(frame)

    print(parsed.payload)
    print(parsed.fin_bit)
    print(parsed.payload_length)
    print(parsed.opcode)


def test3():
    frame = bytearray()
    # finbit of 1, opcode of 8
    frame.append(0b10001000)
    # mask of 1, payload len of 4
    frame.append(0b10000100)

    # mask
    frame.append(0b10110100)
    frame.append(0b01100110)
    frame.append(0b01000010)
    frame.append(0b01111100)

    # payload:
    frame.append(0b10010100)
    frame.append(0b01111110)
    frame.append(0b01010010)
    frame.append(0b01000100)

    parsed = parse_ws_frame(frame)

    print(parsed.payload)
    print(parsed.fin_bit)
    print(parsed.payload_length)
    print(parsed.opcode)

    m_1 = 0b10110100 ^ 0b10010100
    m_2 = 0b01100110 ^ 0b01111110
    m_3 = 0b01000010 ^ 0b01010010
    m_4 = 0b01111100 ^ 0b01000100

    payload = bytearray()
    payload.append(m_1)
    payload.append(m_2)
    payload.append(m_3)
    payload.append(m_4)

    print(parsed.payload)
    print(bytes(payload))
    assert parsed.payload == bytes(payload)


if __name__ == "__main__":
    test3()
