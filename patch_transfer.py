import sys

content = open('transfer.py').read()

import_str = "import time\nfrom utils import zip_folder, unzip_folder, calculate_hash\n\n# Global chat history"
new_import_str = "import time\nimport uuid\nfrom utils import zip_folder, unzip_folder, calculate_hash\n\nactive_transfers = {}\n# Global chat history"
content = content.replace(import_str, new_import_str)

recv_loop = """                    # Open file and receive chunks
                    with open(f"{file_name}", "ab") as f:
                        bytes_received = existing_bytes
                        while bytes_received < file_size:
                            chunk = conn.recv(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                            bytes_received += len(chunk)"""

new_recv_loop = """                    # Open file and receive chunks
                    transfer_id = f"{peer_ip}_{file_name}"
                    active_transfers[transfer_id] = {
                        'peer_ip': peer_ip, 'file_name': file_name, 'direction': 'in',
                        'transferred': existing_bytes, 'total': file_size
                    }
                    with open(f"{file_name}", "ab") as f:
                        bytes_received = existing_bytes
                        while bytes_received < file_size:
                            chunk = conn.recv(65536)
                            if not chunk:
                                break
                            f.write(chunk)
                            bytes_received += len(chunk)
                            active_transfers[transfer_id]['transferred'] = bytes_received
                    
                    if transfer_id in active_transfers:
                        del active_transfers[transfer_id]"""
content = content.replace(recv_loop, new_recv_loop)

send_loop = """            # Send File
            if message_recv == 'READY':
                with open(file_path, "rb") as file:
                    file.seek(int(existing_byte))
                    while True:
                        chunk = file.read(1024)
                        if not chunk:
                            break
                        sender_socket.sendall(chunk)
                print("File data sent successfully.")"""

new_send_loop = """            # Send File
            if message_recv == 'READY':
                transfer_id = f"{target_ip}_{file_name}"
                bytes_sent = int(existing_byte)
                active_transfers[transfer_id] = {
                    'peer_ip': target_ip, 'file_name': file_name, 'direction': 'out',
                    'transferred': bytes_sent, 'total': file_size
                }
                with open(file_path, "rb") as file:
                    file.seek(bytes_sent)
                    while True:
                        chunk = file.read(65536)
                        if not chunk:
                            break
                        sender_socket.sendall(chunk)
                        bytes_sent += len(chunk)
                        active_transfers[transfer_id]['transferred'] = bytes_sent
                
                if transfer_id in active_transfers:
                    del active_transfers[transfer_id]
                print("File data sent successfully.")"""
content = content.replace(send_loop, new_send_loop)

open('transfer.py', 'w').write(content)
