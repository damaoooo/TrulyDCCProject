import socket
import select
import queue


class PhysicalConfig:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 33148
        self.peer = ('127.0.0.1', 34234)
        self.start = b'deadbeef'
        self.end = b'beefdead'


class PhysicalLayer:
    def __init__(self, config: PhysicalConfig, send_queue: queue.Queue, recv_queue: queue.Queue):
        self.config = config
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((config.host, config.port))
        self.send_queue = send_queue
        self.recv_queue = recv_queue

    # Wrap deadbeef with %deadbeef%, if bytes occurs %deadbeef%, then %%deadbeef%%
    # process the % into %%
    # this is to say, if send deadbeef -> %deadbeef%
    # if send %deadbeef% -> %%deadbeef%%
    # if send %%deadbeef% -> %%%deadbeef%%
    def escape(self, send_bytes: bytes):
        send_bytes = send_bytes.replace(self.config.start, b'%' + self.config.start + b'%')
        send_bytes = send_bytes.replace(self.config.end, b'%' + self.config.end + b'%')
        return send_bytes

    def unescape(self, recv_bytes: bytes):
        recv_bytes = recv_bytes.replace(b'%' + self.config.start + b'%', self.config.start)
        recv_bytes = recv_bytes.replace(b'%' + self.config.end + b'%', self.config.end)
        return recv_bytes

    def start(self):
        while 1:
            read_list, write_list, _ = select.select([self.socket], [self.socket], [], __timeout=0.01)
            for read_socket in read_list:
                read_socket: socket.socket
                recv_bytes, _ = read_socket.recvfrom(4096)
                recv_bytes: bytes
                # no data received
                if not recv_bytes:
                    break
                start = recv_bytes.find(self.config.start)
                end = recv_bytes.rfind(self.config.end)
                if start != -1 and end != -1:
                    packet = recv_bytes[start + len(self.config.start): end]
                    # start and end is wrong
                    if not packet:
                        break
                    packet = self.unescape(packet)
                    self.recv_queue.put(packet)
                else:
                    break

            for write_socket in write_list:
                write_socket: socket.socket
                while not self.send_queue.empty():
                    send_bytes = self.send_queue.get()
                    send_bytes = self.escape(send_bytes)
                    write_socket.sendto(send_bytes, self.config.peer)
