from io import BytesIO
import varint
import json

def s2c(original):
    return original

def c2s(original):
    return original

@c2s
class HandshakePacket:
    def __init__(self, protocol_version, server_address, server_port, next_state):
        self.protocol_version = protocol_version
        self.server_address = server_address
        self.server_port = server_port
        self.next_state = next_state

    def __str__(self):
        return f"HandshakePacket(protocol={self.protocol_version}, " + \
               f"server_addr={self.server_address}, " + \
               f"server_port={self.server_port}, " + \
               f"next_state={self.next_state})"

    @classmethod
    def from_stream(cls, stream: BytesIO):
        protocol_version = varint.decode_stream(stream)
        server_address_len = varint.decode_stream(stream)
        server_address = stream.read(server_address_len).decode()
        server_port = int.from_bytes(stream.read(2), "big")
        next_state = varint.decode_stream(stream)

        return HandshakePacket(protocol_version,
                               server_address,
                               server_port,
                               next_state)

@c2s
class RequestPacket:
    def __str__(self):
        return "RequestPacket()"

    @classmethod
    def from_stream(cls, stream: BytesIO):
        return RequestPacket()

@s2c
class ResponsePacket:
    def __init__(self, response):
        self.response = response

    def to_bytes(self):
        return packPacket(
            b"\x00" + \
            packString(json.dumps(self.response, separators=(',', ':')))
        )

@c2s
class LoginStartPacket:
    def __init__(self, username):
        self.username = username

    def __str__(self):
        return f"LoginStartPacket(username={self.username})"

    @classmethod
    def from_stream(cls, stream: BytesIO):
        username_len = varint.decode_stream(stream)
        username = stream.read(username_len).decode()

        return LoginStartPacket(username)

@s2c
class DisconnectPacket:
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return f"DisconnectPacket(reason={self.reason})"

    def to_bytes(self):
        return packPacket(
            b"\x00" + \
            packString(json.dumps(self.reason, separators=(",", ":")))
        )

@c2s
class PingPacket:
    def __init__(self, payload):
        self.payload = payload

    def __str__(self):
        return f"PingPacket(payload={self.payload})"

    @classmethod
    def from_stream(cls, stream: BytesIO):
        payload = stream.read(8)

        return PingPacket(payload)

@s2c
class PongPacket:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __str__(self):
        return f"PongPacket(payload={self.payload})"

    def to_bytes(self) -> bytes:
        return packPacket(b'\x01' + self.payload)

def packString(data: str) -> bytes:
    return varint.encode(len(data)) + bytes(data, 'utf-8')

def packPacket(data: bytes) -> bytes:
    return varint.encode(len(data)) + data