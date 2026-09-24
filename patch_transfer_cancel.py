import sys

content = open('transfer.py').read()

# Receiver loop
recv_loop = """                    with open(f"{file_name}", "ab") as f:
                        bytes_received = existing_bytes
                        while bytes_received < file_size:
                            chunk = conn.recv(65536)
                            if not chunk:
                                break
                            f.write(chunk)
                            bytes_received += len(chunk)
                            active_transfers[transfer_id]['transferred'] = bytes_received"""

new_recv_loop = """                    with open(f"{file_name}", "ab") as f:
                        bytes_received = existing_bytes
                        while bytes_received < file_size:
                            if active_transfers.get(transfer_id, {}).get('cancelled'):
                                print("Receiver cancelled transfer.")
                                break
                            
                            chunk = conn.recv(65536)
                            if not chunk:
                                break
                            f.write(chunk)
                            bytes_received += len(chunk)
                            if transfer_id in active_transfers:
                                active_transfers[transfer_id]['transferred'] = bytes_received"""
content = content.replace(recv_loop, new_recv_loop)

# Sender loop
send_loop = """                with open(file_path, "rb") as file:
                    file.seek(bytes_sent)
                    while True:
                        chunk = file.read(65536)
                        if not chunk:
                            break
                        sender_socket.sendall(chunk)
                        bytes_sent += len(chunk)
                        active_transfers[transfer_id]['transferred'] = bytes_sent"""

new_send_loop = """                with open(file_path, "rb") as file:
                    file.seek(bytes_sent)
                    while True:
                        if active_transfers.get(transfer_id, {}).get('cancelled'):
                            print("Sender cancelled transfer.")
                            raise Exception("Cancelled by user")
                            
                        chunk = file.read(65536)
                        if not chunk:
                            break
                        sender_socket.sendall(chunk)
                        bytes_sent += len(chunk)
                        if transfer_id in active_transfers:
                            active_transfers[transfer_id]['transferred'] = bytes_sent"""
content = content.replace(send_loop, new_send_loop)

open('transfer.py', 'w').write(content)
