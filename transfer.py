import os
import shutil
import socket 
import time
from utils import zip_folder, unzip_folder, calculate_hash

# Global chat history to store messages and file events
# Format: {'peer_ip': ip, 'type': 'text'|'file', 'direction': 'in'|'out', 'content': string, 'timestamp': float}
chat_history = []

class FileTransfer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
    
    def server(self):
        reciever_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        reciever_socket.bind((self.host, self.port))
        reciever_socket.listen(5)
        print(f"Listening for connections on {self.host}:{self.port}...")
        while True:
            conn, addr = reciever_socket.accept()
            peer_ip = addr[0]
            print(f"Connected to {peer_ip}")
            try:
            
                raw_header = conn.recv(1024)
                header = raw_header.decode('utf-8')
                
                if header:
                    if header.startswith('CHAT|'):
                        _, msg_content = header.split('|', 1)
                        chat_history.append({
                            'peer_ip': peer_ip,
                            'type': 'text',
                            'direction': 'in',
                            'content': msg_content,
                            'timestamp': time.time()
                        })
                        print(f"Received message from {peer_ip}: {msg_content}")
                        conn.sendall(b'EXIT')
                        continue

                    file_name, file_size, file_hash = header.split('|')
                    file_size = int(file_size)
                    print(f"Receiving file: {file_name} of size: {file_size} bytes")

                    if os.path.exists(file_name):

                        existing_bytes = os.path.getsize(file_name)
                    else:
                        existing_bytes = 0

                    # Acknowledge the header
                    conn.sendall(f"READY|{existing_bytes}".encode('utf-8'))


                    # Open file and receive chunks
                    with open(f"{file_name}", "ab") as f:
                        bytes_received = existing_bytes
                        while bytes_received < file_size:
                            chunk = conn.recv(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                            bytes_received += len(chunk)

                    received_hash = calculate_hash(file_name)
                    if received_hash == file_hash:
                        print(f"File received successfully and verified.")
                        
                        chat_history.append({
                            'peer_ip': peer_ip,
                            'type': 'file',
                            'direction': 'in',
                            'content': os.path.basename(file_name),
                            'timestamp': time.time()
                        })

                        if file_name.endswith('.zip'):
                            received_folder = unzip_folder(file_name)
                    else:
                        print(f"File received but verification failed.")
                        os.remove(file_name)
            except Exception as e:
                print("connection with cient lost: ", e)
            finally:
                
                # Send exit confirmation so the client knows it's safe to hang up
                conn.sendall(b'EXIT')
                
                conn.close()

    def send_message(self, target_ip, message):
        sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Sending message to {target_ip}...")
        try:
            sender_socket.connect((target_ip, self.port))
            header = f"CHAT|{message}"
            sender_socket.send(header.encode('utf-8'))
            
            # Wait for Server to confirm receipt
            exit_message = sender_socket.recv(1024).decode('utf-8')
            if exit_message == 'EXIT':
                print("Message sent successfully.")
                chat_history.append({
                    'peer_ip': target_ip,
                    'type': 'text',
                    'direction': 'out',
                    'content': message,
                    'timestamp': time.time()
                })
        except Exception as e:
            print("Message transfer failed: ", e)
        finally:
            sender_socket.close()

    def send_file(self, target_ip, file_path):
        sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(f"Connecting to {target_ip}...")
        try:
            sender_socket.connect((target_ip, self.port))

            if os.path.isdir(file_path):
                file_path = zip_folder(file_path)
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_hash = calculate_hash(file_path)

            # Send Header
            header = f"{file_name}|{file_size}|{file_hash}"
            sender_socket.send(header.encode('utf-8')) 
            
            # Wait for ACK
            raw_data = sender_socket.recv(1024)
            message = raw_data.decode('utf-8')
            message_recv, existing_byte = message.split('|')
            # Send File
            if message_recv == 'READY':
                with open(file_path, "rb") as file:
                    file.seek(int(existing_byte))
                    while True:
                        chunk = file.read(1024)
                        if not chunk:
                            break
                        sender_socket.sendall(chunk)
                print("File data sent successfully.")
                chat_history.append({
                    'peer_ip': target_ip,
                    'type': 'file',
                    'direction': 'out',
                    'content': file_name,
                    'timestamp': time.time()
                })

            # Wait for Server to confirm receipt before closing
            exit_message = sender_socket.recv(1024).decode('utf-8')
            if exit_message == 'EXIT':
                print("Server confirmed receipt. Disconnecting.")
        except Exception as e:
            print("Transfer failed: ", e)
        finally:
            sender_socket.close()