import sys
content = open('web_app.py').read()

init_str = """discovery = None # Will be initialized in main
transfer = FileTransfer()"""

new_init_str = """discovery = None # Will be initialized in main
transfer = FileTransfer()
known_peers = {} # Global dict of known peers (IP -> Alias)"""
content = content.replace(init_str, new_init_str)

get_peers_str = """        elif path == '/api/peers':
            # Collect peers from discovery (if any) and chat_history
            peers_dict = {}
            # We don't have direct access to discovered_peers here, but we can just use chat_history
            for msg in chat_history:
                ip = msg['peer_ip']
                if ip not in peers_dict:
                    peers_dict[ip] = "Unknown" # Or fetch from known_peers if we implement it
            
            peer_list = [{"ip": ip, "alias": alias} for ip, alias in peers_dict.items()]
            self._send_json({"peers": peer_list})"""

new_get_peers_str = """        elif path == '/api/peers':
            # Collect peers from discovery (if any) and chat_history
            for msg in chat_history:
                ip = msg['peer_ip']
                if ip not in known_peers:
                    known_peers[ip] = "Unknown"
            
            peer_list = [{"ip": ip, "alias": alias} for ip, alias in known_peers.items()]
            self._send_json({"peers": peer_list})"""
content = content.replace(get_peers_str, new_get_peers_str)

post_scan_str = """        if path == '/api/scan':
            print("[Web GUI] Scanning network for P2P peers...")
            try:
                discovered_peers = discovery.scan_network()
            except Exception as e:
                print(f"[Web GUI] Scan error (offline or no broadcast route): {e}")
                discovered_peers = []
            print(f"[Web GUI] Discovered peers: {discovered_peers}")
            self._send_json({"peers": discovered_peers})"""

new_post_scan_str = """        if path == '/api/scan':
            print("[Web GUI] Scanning network for P2P peers...")
            try:
                discovered_peers = discovery.scan_network()
                for p in discovered_peers:
                    known_peers[p['ip']] = p['alias']
            except Exception as e:
                print(f"[Web GUI] Scan error (offline or no broadcast route): {e}")
                discovered_peers = []
            print(f"[Web GUI] Discovered peers: {discovered_peers}")
            
            # Also merge with any from chat history
            for msg in chat_history:
                ip = msg['peer_ip']
                if ip not in known_peers:
                    known_peers[ip] = "Unknown"
            
            merged_peers = [{"ip": ip, "alias": alias} for ip, alias in known_peers.items()]
            self._send_json({"peers": merged_peers})"""
content = content.replace(post_scan_str, new_post_scan_str)

open('web_app.py', 'w').write(content)
