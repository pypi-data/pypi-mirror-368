import socket


class NullProto(object):
    def __init__(self, *args, **kwargs):
        pass

    def send(self, *args, **kwargs):
        pass


class BaseUdpProto(object):
    """The base class for the udp client protocol."""

    def __init__(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.addr = (host, port)
        self.sock = sock

    def sendto(self, data):
        self.sock.sendto(data, self.addr)

    def send(self, data):
        raise NotImplementedError('Please implement this method')

    def __del__(self):
        self.sock.close()


class UdpProto(BaseUdpProto):

    def send(self, data):
        try:
            self.sendto(data)
        except (socket.error, RuntimeError):
            pass
