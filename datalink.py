import queue
from zlib import crc32
from utils import IPLayerProtocol


class DatalinkLayerConfig:
    def __init__(self):
        self.mac = b'\xaa\xbb\xcc\xdd\x00\x00\x00'


class DatalinkLayerPacket:
    def __init__(self):
        self.sourceMAC = b'\x00' * 6
        self.destinationMAC = b'\x00' * 6
        self.protocol = IPLayerProtocol.ARP
        self.checksum = b'\x00' * 4
        self.pdu = b''

    def deserialize(self, sdu: bytes):
        source_mac = sdu[:6]
        self.sourceMAC = source_mac
        sdu = sdu[6:]
        destination_mac = sdu[:6]
        self.destinationMAC = destination_mac
        sdu = sdu[6:]
        protocol = sdu[:2]
        protocol = int.from_bytes(protocol, 'big', signed=False)
        self.protocol = protocol
        sdu = sdu[2:]
        checksum = sdu[-4:]
        self.checksum = checksum
        pdu = sdu[:-4]
        self.pdu = pdu
        return self.get_crc() == self.checksum

    def get_crc(self):
        checksum = crc32(self.sourceMAC + self.destinationMAC + int.to_bytes(self.protocol, 2, 'big') + self.pdu)
        return checksum.to_bytes(4, 'big', signed=False)

    def serialize(self):
        checksum = self.get_crc()
        return self.sourceMAC + self.destinationMAC + int.to_bytes(self.protocol, 2, 'big') + self.pdu + checksum


class DatalinkLayer:
    def __init__(self, config: DatalinkLayerConfig, phy_send_queue: queue.Queue,
                 phy_recv_queue: queue.Queue, ip_send_queue: queue.Queue,
                 ip_recv_queue: queue.Queue):
        self.config = config
        self.phy_send_queue = phy_send_queue
        self.phy_recv_queue = phy_recv_queue
        self.ip_send_queue = ip_send_queue
        self.ip_recv_queue = ip_recv_queue

    def send(self):
        destination, pdu, protocol = self.ip_send_queue.get()
        new_packet = DatalinkLayerPacket()
        new_packet.sourceMAC = self.config.mac
        new_packet.destinationMAC = destination
        new_packet.pdu = pdu
        new_packet.protocol = protocol
        sdu = new_packet.serialize()
        self.phy_send_queue.put(sdu)

    def recv(self):
        if not self.phy_recv_queue.empty():
            sdu = self.phy_recv_queue.get()
            new_packet = DatalinkLayerPacket()
            if new_packet.deserialize(sdu):
                if new_packet.destinationMAC == self.config.mac or new_packet.destinationMAC == b'\xff'*6:
                    self.ip_recv_queue.put((new_packet.protocol, new_packet.pdu))

    def start(self):
        while 1:
            if not self.ip_send_queue.empty():
                self.send()

            if not self.phy_recv_queue.empty():
                self.recv()


