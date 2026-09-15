import socket

class NetworkDiscovery:
    def __init__(self, host='0.0.0.0', port = 50000):
            self.host = host
            self.port = port

    def start_listner(self):
        discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        discovery_socket.bind(('0.0.0.0', 50000))
        while True:
            data, addr = discovery_socket.recvfrom(1024)
            if data.decode('utf-8') == 'P2P_DISCOVER':
                discovery_socket.sendto(b'P2P_RESPONSE', addr)

    def scan_network(self):
        socket.SOCK_DGRAM
        sock_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock_sock.settimeout(2.0)
        sock_sock.sendto(b"P2P_DISCOVER", ('<broadcast>', 50000))
        discovered_peers = []
        try:
            while True:
                data, addr = sock_sock.recvfrom(1024)
                if data.decode('utf-8') == 'P2P_RESPONSE':
                    discovered_peers.append(addr[0])
        except socket.timeout:
            pass
        return discovered_peers
        