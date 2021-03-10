from packet import DisconnectPacket, HandshakePacket, LoginStartPacket, PingPacket, PongPacket, ResponsePacket, packString
import varint
import uuid
import random
from minecraft import protips
from io import BytesIO

class Connection:

    '''
    0 for initial state
    1 for status
    2 for login
    '''
    state = 0
    recent_handshake_packet = None

    def __init__(self, addr):
        self.addr = addr

    def decode_and_response(self, stream: BytesIO):
        while stream.readable():
            length = varint.decode_stream(stream)
            data_stream = BytesIO(stream.read(length))
            packet_id = varint.decode_stream(data_stream)

            if packet_id == 0 and self.state == 0:
                self.recent_handshake_packet = \
                    res = HandshakePacket.from_stream(data_stream)
                print(res)
                self.state = res.next_state
            elif packet_id == 0 and self.state == 1:
                response = None

                if self.recent_handshake_packet.server_address == "localhost":
                    response = {
                        "version": {
                            "name": "2021 TRUSTEALTH PLAYGROUND",
                            "protocol": self.recent_handshake_packet.protocol_version
                        },
                        "players": {
                            "max": 2021,
                            "online": 0,
                            "sample": [
                                {
                                    "name": "§aCongratulations!",
                                    "id": str(uuid.uuid4())
                                }
                            ]
                        },
                        "description": {
                            "text": "§bWell done. Here's your flag: §eFLAG{M1n3cr4ft_15_da_b3st_gam3_ever}§r"
                        }
                    }
                else:
                    response = {
                        "version": {
                            "name": "2021 TRUSTREALTH PLAYGROUND",
                            "protocol": 1
                        },
                        "players": {
                            "max": 2021,
                            "online": 0,
                            "sample": [
                                {
                                    "name": "You should connect with localhost.",
                                    "id": str(uuid.uuid4())
                                }
                            ]
                        },
                        "description": {
                            "text": "§eWelcome to Minecraft.\nHover on §c2021 TRUSTEALTH PLAYGROUND§e for more information."
                        }
                    }

                return ResponsePacket(response).to_bytes(), False

            elif packet_id == 0 and self.state == 2:
                self.state = 0
                
                res = LoginStartPacket.from_stream(data_stream)
                print(res)

                def random_color():
                    return hex(random.choice(range(64, 256)))[2:]

                return DisconnectPacket([
                    {
                        "text": "Login is not required.\nYou should use \"Add Server\" to solve problem.\n\n"
                    },
                    {
                        "text": f"PRO TIP: {random.choice(protips)}",
                        "color": f"#{random_color()}{random_color()}{random_color()}"
                    }
                ]).to_bytes(), True

            elif packet_id == 1 and self.state == 1:
                res = PingPacket.from_stream(data_stream)
                print(res)
                return PongPacket(res.payload).to_bytes(), True
            else:
                return None, True
