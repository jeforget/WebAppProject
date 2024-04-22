import base64
import hashlib


def compute_accept(web_str: str):
    guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    # Get the sha1 of the concatenation of web_str and guid
    base = hashlib.sha1(web_str + guid)

    # Encode with base64
    sixty4 = base64.b64encode(base)

    # return
    return sixty4

def parse_ws_frame(frame):
    output = Frame
    output.finbit = (frame[0] & 0b10000000) >> 7  # 0 >> 7 = 0, 128 (256?) >> 7 = 1
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

    output.payload = frame

    if masking_bit != 0:
        for index in range(len(output.payload)):  # starts at 0, goes to len - 1
            mask_index = index % 4
            if mask_index == 0:
                mask_index = 4
            mask_index -= 1
            output.payload[index] = output.payload[index] ^ mask[mask_index]

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
    byt = b'0123456789'
    print(byt)
    byt2 = b'987654321'

    byts = b'1234567890'

    # 1 in binary is 00000001 and 128 is 10000000, so 1 & 128 = 00000000
    # for i in range(len(byt)):
    #     if i > 7:
    #         mask = i % 4 + 1
    #         print("use mask " + str(mask))
    #     else:
    #         print("no mask")


if __name__ == "__main__":
    test1()
