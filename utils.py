from enum import Enum, unique


@unique
class IPLayerProtocol(Enum):
    ARP = 0
    IPV4 = 1
    ICMP = 2
