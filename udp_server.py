import socket
import os
import sys

PORT = 8080
HOST = '127.0.0.1'
BUFFER_SIZE = 1024 # Max size to receive (filename)
CHUNK_SIZE = 1000  # Size of file data per packet
ENCODING = 'utf-8'
SEQUENCE_HEADER_LEN = 5 # 4 digits for seq num + 1 colon (e.g., "0001:")

def main():
    """Main function to set up and run the UDP server."""
    try:
        # Create UDP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((HOST, PORT))
        print(f"UDP File Server listening on {HOST}:{PORT}...")
    except socket.error as e:
        print(f"Failed to set up server: {e}")
        sys.exit(1)

    while True:
        print("\nWaiting for client request (filename)...")
        
        try:
            # 1. Receive filename and client address
            data, client_address = server_socket.recvfrom(BUFFER_SIZE)
            filename = data.decode(ENCODING).strip()
            print(f"Received request from {client_address[0]}:{client_address[1]} for file: '{filename}'")

            # 2. Attempt to check and open the file
            if not os.path.exists(filename) or not os.path.isfile(filename):
                # File not found: Send error message
                error_msg = "ERROR: File Not Found."
                server_socket.sendto(error_msg.encode(ENCODING), client_address)
                print(f"Sent {error_msg}")
                continue

            # File found:
            file_size = os.path.getsize(filename)
            print(f"File found (Size: {file_size} bytes). Sending content in chunks...")

            sequence_number = 1
            
            # 3. Read file in binary mode and send chunks
            with open(filename, 'rb') as f:
                while True:
                    bytes_read = f.read(CHUNK_SIZE)
                    if not bytes_read:
                        break # End of file

                    # Construct the packet: [Seq Num (4 digits)]:[Data]
                    seq_header = f"{sequence_number:04d}:".encode(ENCODING)
                    packet_data = seq_header + bytes_read
                    
                    server_socket.sendto(packet_data, client_address)
                    sequence_number += 1
            
            # 4. Send the completion marker
            completion_msg = f"{sequence_number:04d}:FILE_TRANSFER_COMPLETE".encode(ENCODING)
            server_socket.sendto(completion_msg, client_address)
            
            print(f"Transmission complete. Total chunks sent: {sequence_number - 1}")

        except KeyboardInterrupt:
            print("\nServer shutting down.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

    server_socket.close()

if __name__ == "__main__":
    main()

