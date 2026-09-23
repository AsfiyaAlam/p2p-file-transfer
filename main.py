import threading

from discovery import NetworkDiscovery
from transfer import FileTransfer

def main():
    alias = input("Enter device alias (leave blank for default hostname): ").strip()
    discovery = NetworkDiscovery(alias=alias if alias else None)
    transfer = FileTransfer()

    discovery_thread = threading.Thread(target=discovery.start_listner, daemon = True)
    server_thread = threading.Thread(target=transfer.server, daemon = True)
    discovery_thread.start()
    server_thread.start()

    while True:
        print("\n--- P2P File Transfer ---")
        print("1. Send a File/Folder")
        print("2. Exit Program")
        
        choice = input("Enter choice (1/2): ")
        
        if choice == '1':
            discovered_peers = discovery.scan_network()
            if not discovered_peers:
                print("no peer found")
                continue
            print("\nDiscovered Peers:")
            for index, peer in enumerate(discovered_peers, start=1):
                print(f"{index}. {peer['ip']} (Alias: {peer['alias']})")

            peer_choice = int(input("Enter the number of the peer to connect to: ")) - 1

            target_ip = discovered_peers[peer_choice]['ip']
            file_path = input("Enter the file path: ")
            transfer.send_file(target_ip, file_path)
        elif choice == '2':
            print("Shutting down node...")
            break
        else:
            print("Invalid choice.")
    


main()