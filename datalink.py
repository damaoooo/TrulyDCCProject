import queue


class DatalinkLayerConfig:
    def __init__(self):
        self.mac = b'\xaa\xbb\xcc\xdd\x00\x00\x00'

class DatalinkLayerPDU:
    def __init__(self):
        pass

class DatalinkLayer:
    def __init__(self, config: DatalinkLayerConfig, phy_send_queue: queue.Queue,
                 phy_recv_queue: queue.Queue, ip_send_queue: queue.Queue,
                 ip_recv_queue: queue.Queue):
        self.config = config
        self.phy_send_queue = phy_send_queue
        self.phy_recv_queue = phy_recv_queue
        self.ip_send_queue = ip_send_queue
        self.ip_recv_queue = ip_recv_queue


