import socket
import select


class PhysicalConfig:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 33148
        self.start = b'deadbeef'
        self.end = b'beefdead'


class PhysicalLayer:
    def __init__(self, config: PhysicalConfig):
        self.config = config
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((config.host, config.port))

    def start(self):
        while 1:
            read_list, write_list, _ = select.select([self.socket], [self.socket], [self.socket], __timeout=0.01)
