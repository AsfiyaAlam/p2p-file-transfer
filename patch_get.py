import sys

content = open('web_app.py').read()

import_str = "from transfer import FileTransfer\n"
new_import_str = "from transfer import FileTransfer, chat_history\nfrom urllib.parse import parse_qs\n"
content = content.replace(import_str, new_import_str)

get_logs_str = """        elif path == '/api/logs':
            self._send_json({"logs": capturer.get_logs()})"""
new_get_logs_str = """        elif path == '/api/logs':
            self._send_json({"logs": capturer.get_logs()})

        elif path == '/api/chat':
            query = parse_qs(parsed.query)
            peer_ip = query.get('peer', [''])[0]
            if not peer_ip:
                self._send_json({"error": "peer parameter required"}, status=400)
                return
            messages = [msg for msg in chat_history if msg['peer_ip'] == peer_ip]
            self._send_json({"messages": messages})"""
content = content.replace(get_logs_str, new_get_logs_str)

post_logs_clear = """        elif path == '/api/logs/clear':
            capturer.clear()
            self._send_json({"status": "cleared"})"""
new_post_logs_clear = """        elif path == '/api/logs/clear':
            capturer.clear()
            self._send_json({"status": "cleared"})

        elif path == '/api/chat':
            try:
                payload = json.loads(body.decode('utf-8'))
                target_ip = payload.get('target_ip')
                message = payload.get('message')
                if not target_ip or not message:
                    self._send_json({"status": "error", "message": "target_ip and message required"}, status=400)
                    return
                print(f"[Web GUI] Sending message to {target_ip}")
                transfer.send_message(target_ip, message)
                self._send_json({"status": "success"})
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, status=500)"""
content = content.replace(post_logs_clear, new_post_logs_clear)

open('web_app.py', 'w').write(content)
