"""
Module: 'lwip' on micropython-v1.22.1-rp2-RPI_PICO_W
"""
# MCU: {'family': 'micropython', 'version': '1.22.1', 'build': '', 'ver': '1.22.1', 'port': 'rp2', 'board': 'RPI_PICO_W', 'cpu': 'RP2040', 'mpy': 'v6.2', 'arch': 'armv6m'}
# Stubber: v1.17.1
from __future__ import annotations
from _typeshed import Incomplete

SOCK_STREAM: int = 1
SOCK_RAW: int = 3
SOCK_DGRAM: int = 2
SOL_SOCKET: int = 1
SO_BROADCAST: int = 32
SO_REUSEADDR: int = 4
AF_INET6: int = 10
AF_INET: int = 2
IP_DROP_MEMBERSHIP: int = 1025
IPPROTO_IP: int = 0
IP_ADD_MEMBERSHIP: int = 1024

def reset(*args, **kwargs) -> Incomplete: ...
def print_pcbs(*args, **kwargs) -> Incomplete: ...
def getaddrinfo(*args, **kwargs) -> Incomplete: ...
def callback(*args, **kwargs) -> Incomplete: ...

class socket:
    def recvfrom(self, *args, **kwargs) -> Incomplete: ...
    def recv(self, *args, **kwargs) -> Incomplete: ...
    def makefile(self, *args, **kwargs) -> Incomplete: ...
    def listen(self, *args, **kwargs) -> Incomplete: ...
    def settimeout(self, *args, **kwargs) -> Incomplete: ...
    def sendall(self, *args, **kwargs) -> Incomplete: ...
    def setsockopt(self, *args, **kwargs) -> Incomplete: ...
    def setblocking(self, *args, **kwargs) -> Incomplete: ...
    def sendto(self, *args, **kwargs) -> Incomplete: ...
    def readline(self, *args, **kwargs) -> Incomplete: ...
    def readinto(self, *args, **kwargs) -> Incomplete: ...
    def read(self, *args, **kwargs) -> Incomplete: ...
    def close(self, *args, **kwargs) -> Incomplete: ...
    def connect(self, *args, **kwargs) -> Incomplete: ...
    def send(self, *args, **kwargs) -> Incomplete: ...
    def bind(self, *args, **kwargs) -> Incomplete: ...
    def accept(self, *args, **kwargs) -> Incomplete: ...
    def write(self, *args, **kwargs) -> Incomplete: ...
    def __init__(self, *argv, **kwargs) -> None: ...
