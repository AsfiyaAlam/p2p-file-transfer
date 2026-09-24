import os
import sys
import json
import socket
import threading
import time
import email
import email.policy
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from discovery import NetworkDiscovery
from transfer import FileTransfer, chat_history, active_transfers
from urllib.parse import parse_qs

# Global log capture so UI can display live progress
class LogCapturer:
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout
        self.logs = []
        self.lock = threading.Lock()

    def write(self, text):
        self.original_stdout.write(text)
        stripped = text.strip()
        if stripped:
            with self.lock:
                timestamp = time.strftime('%H:%M:%S')
                self.logs.append(f"[{timestamp}] {stripped}")
                if len(self.logs) > 150:
                    self.logs.pop(0)

    def flush(self):
        self.original_stdout.flush()

    def get_logs(self):
        with self.lock:
            return list(self.logs)

    def clear(self):
        with self.lock:
            self.logs.clear()


capturer = LogCapturer(sys.stdout)
sys.stdout = capturer

# Initialize existing engines (completely untouched)
discovery = None # Will be initialized in main
transfer = FileTransfer()
known_peers = {} # Global dict of known peers (IP -> Alias)

# Staging directory for browser uploads
UPLOAD_DIR = os.path.abspath("temp_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Project root for templates and inbox
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(BASE_DIR, "templates", "index.html")

# System excluded files for the received inbox
EXCLUDED_NAMES = {
    "discovery.py", "main.py", "transfer.py", "utils.py", "web_app.py",
    ".git", ".gitignore", "templates", "__pycache__", "temp_uploads"
}


def get_local_ip():
    """Determines the LAN IP address of this device."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return '127.0.0.1'


class P2PWebHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/' or path == '/index.html':
            if os.path.exists(TEMPLATE_FILE):
                with open(TEMPLATE_FILE, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "Template index.html not found.")

        elif path == '/api/status':
            self._send_json({
                "host_ip": get_local_ip(),
                "ports": {"discovery": 50000, "transfer": 12345, "web": 5000}
            })

        elif path == '/api/logs':
            self._send_json({"logs": capturer.get_logs()})

        elif path == '/api/peers':
            # Collect peers from discovery (if any) and chat_history
            for msg in chat_history:
                ip = msg['peer_ip']
                if ip not in known_peers:
                    known_peers[ip] = "Unknown"
            
            peer_list = [{"ip": ip, "alias": alias} for ip, alias in known_peers.items()]
            self._send_json({"peers": peer_list})

        elif path == '/api/progress':
            self._send_json({"transfers": list(active_transfers.values())})
            
        elif path == '/api/chat':
            query = parse_qs(parsed.query)
            peer_ip = query.get('peer', [''])[0]
            if not peer_ip:
                self._send_json({"error": "peer parameter required"}, status=400)
                return
            messages = [msg for msg in chat_history if msg['peer_ip'] == peer_ip]
            self._send_json({"messages": messages})

        elif path == '/api/received':
            files = []
            for item in os.listdir(BASE_DIR):
                if item not in EXCLUDED_NAMES and not item.startswith('.'):
                    full_path = os.path.join(BASE_DIR, item)
                    stat = os.stat(full_path)
                    mod_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime))
                    size = stat.st_size if os.path.isfile(full_path) else 0
                    files.append({
                        "name": item,
                        "size": size,
                        "is_dir": os.path.isdir(full_path),
                        "modified": mod_time
                    })
            files.sort(key=lambda x: x['modified'], reverse=True)
            self._send_json({"files": files})

        else:
            self.send_error(404, "Endpoint not found.")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        if path == '/api/scan':
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
            self._send_json({"peers": merged_peers})

        elif path == '/api/logs/clear':
            capturer.clear()
            self._send_json({"status": "cleared"})

        elif path == '/api/cancel':
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
                self._send_json({"status": "error", "message": str(e)}, status=500)

        elif path == '/api/send':
            content_type = self.headers.get('Content-Type', '')
            target_ip = None
            file_to_send = None

            try:
                # Handle JSON payload (local disk path)
                if 'application/json' in content_type:
                    payload = json.loads(body.decode('utf-8'))
                    target_ip = payload.get('target_ip')
                    file_to_send = payload.get('file_path')

                    if not file_to_send or not os.path.exists(file_to_send):
                        self._send_json({
                            "status": "error",
                            "message": f"Path '{file_to_send}' does not exist on disk."
                        }, status=400)
                        return

                # Handle Multipart form data (browser file upload)
                elif 'multipart/form-data' in content_type:
                    raw_headers = f"Content-Type: {content_type}\r\n\r\n".encode('utf-8')
                    msg = email.message_from_bytes(raw_headers + body, policy=email.policy.default)

                    for part in msg.iter_parts():
                        name = part.get_param('name', header='content-disposition')
                        filename = part.get_filename()

                        if filename:
                            file_payload = part.get_payload(decode=True)
                            safe_name = os.path.basename(filename)
                            file_to_send = os.path.join(UPLOAD_DIR, safe_name)
                            with open(file_to_send, 'wb') as f:
                                f.write(file_payload)
                        elif name == 'target_ip':
                            target_ip = part.get_payload(decode=True).decode('utf-8').strip()

                if not target_ip:
                    self._send_json({"status": "error", "message": "Missing target IP address."}, status=400)
                    return

                if not file_to_send:
                    self._send_json({"status": "error", "message": "No file specified or uploaded."}, status=400)
                    return

                print(f"[Web GUI] Dispatching transfer to {target_ip} with file: {file_to_send}")
                transfer.send_file(target_ip, file_to_send)

                self._send_json({
                    "status": "success",
                    "message": f"Transferred {os.path.basename(file_to_send)} successfully to {target_ip}."
                })

            except Exception as e:
                print(f"[Web GUI] Transfer error: {e}")
                self._send_json({"status": "error", "message": f"Transfer failed: {str(e)}"}, status=500)

        else:
            self.send_error(404, "Endpoint not found.")

    def log_message(self, format, *args):
        # Suppress routine HTTP request logging to keep console clean
        pass


def start_app(port=5000, alias=None):
    global discovery
    discovery = NetworkDiscovery(alias=alias)
    # 1. Start background P2P listener threads (untouched functionality)
    discovery_thread = threading.Thread(target=discovery.start_listner, daemon=True)
    server_thread = threading.Thread(target=transfer.server, daemon=True)
    discovery_thread.start()
    server_thread.start()

    # 2. Start Web Server (with fallback if port is in use)
    host_ip = get_local_ip()
    httpd = None
    for p in [port, 5001, 8000, 8080]:
        try:
            server_address = ('0.0.0.0', p)
            httpd = ThreadingHTTPServer(server_address, P2PWebHandler)
            port = p
            break
        except OSError:
            continue

    if not httpd:
        print(f"Error: Could not bind to port {port} or fallback ports.")
        return

    print("=" * 60)
    print("🌐 P2P File Transfer Web Application Running!")
    print(f"👉 Local Access:   http://localhost:{port}")
    print(f"👉 LAN Network:    http://{host_ip}:{port}")
    print(f"👉 Device Alias:   {discovery.alias}")
    print("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down web application...")
    finally:
        httpd.server_close()


if __name__ == '__main__':
    port = 5000
    alias = None
    args = sys.argv[1:]
    
    # Simple CLI argument parsing
    if args and args[0].isdigit():
        port = int(args.pop(0))
    
    if '--alias' in args:
        idx = args.index('--alias')
        if idx + 1 < len(args):
            alias = args[idx + 1]
            
    start_app(port=port, alias=alias)
