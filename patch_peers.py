import sys

content = open('web_app.py').read()

get_chat_str = """        elif path == '/api/chat':
            query = parse_qs(parsed.query)"""

new_get_peers_str = """        elif path == '/api/peers':
            # Collect peers from discovery (if any) and chat_history
            peers_dict = {}
            # We don't have direct access to discovered_peers here, but we can just use chat_history
            for msg in chat_history:
                ip = msg['peer_ip']
                if ip not in peers_dict:
                    peers_dict[ip] = "Unknown" # Or fetch from known_peers if we implement it
            
            peer_list = [{"ip": ip, "alias": alias} for ip, alias in peers_dict.items()]
            self._send_json({"peers": peer_list})

        elif path == '/api/chat':
            query = parse_qs(parsed.query)"""

content = content.replace(get_chat_str, new_get_peers_str)
open('web_app.py', 'w').write(content)
