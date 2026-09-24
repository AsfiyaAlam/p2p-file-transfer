import sys

content = open('web_app.py').read()

api_chat_str = """        elif path == '/api/chat':
            try:
                payload = json.loads(body.decode('utf-8'))"""

new_api_cancel_str = """        elif path == '/api/cancel':
            try:
                payload = json.loads(body.decode('utf-8'))
                transfer_id = payload.get('transfer_id')
                if not transfer_id or transfer_id not in active_transfers:
                    self._send_json({"status": "error", "message": "Invalid transfer ID"}, status=400)
                    return
                
                t_info = active_transfers[transfer_id]
                target_ip = t_info['peer_ip']
                f_name = t_info['file_name']
                
                active_transfers[transfer_id]['cancelled'] = True
                
                # Run send_message in a background thread to avoid blocking the API response
                # and to give the sockets a moment to close.
                def notify_peer():
                    time.sleep(1.0) # Wait for sockets to drop
                    try:
                        transfer.send_message(target_ip, f"🚫 Transfer of '{f_name}' was cancelled by the peer.")
                    except:
                        pass
                
                threading.Thread(target=notify_peer, daemon=True).start()
                
                self._send_json({"status": "success"})
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, status=500)

        elif path == '/api/chat':
            try:
                payload = json.loads(body.decode('utf-8'))"""

content = content.replace(api_chat_str, new_api_cancel_str)
open('web_app.py', 'w').write(content)
