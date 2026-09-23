import socket

class NetworkDiscovery:
    def __init__(self, host='0.0.0.0', port=50000, alias=None):
        self.host = host
        self.port = port
        self.alias = alias or socket.gethostname()

    def start_listner(self):
        discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        discovery_socket.bind(('0.0.0.0', 50000))
        while True:
            data, addr = discovery_socket.recvfrom(1024)
            if data.decode('utf-8') == 'P2P_DISCOVER':
                response = f'P2P_RESPONSE:{self.alias}'
                discovery_socket.sendto(response.encode('utf-8'), addr)

    def scan_network(self):
        sock_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock_sock.settimeout(3.0)
        sock_sock.sendto(b"P2P_DISCOVER", ('<broadcast>', 50000))
        discovered_peers = {}
        try:
            while True:
                data, addr = sock_sock.recvfrom(1024)
                decoded_data = data.decode('utf-8')
                if decoded_data.startswith('P2P_RESPONSE:'):
                    alias = decoded_data.split(':', 1)[1]
                    discovered_peers[addr[0]] = alias
        except socket.timeout:
            pass
        return [{'ip': ip, 'alias': alias} for ip, alias in discovered_peers.items()]
        