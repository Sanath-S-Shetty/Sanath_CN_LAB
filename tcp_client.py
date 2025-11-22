import socket
import sys

PORT = 8080
HOST = '127.0.0.1'
BUFFER_SIZE = 1024
ENCODING = 'utf-8'

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]

    print(f"Attempting to request file: '{filename}' from {HOST}:{PORT}")

    # 1. Create socket file descriptor
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        print("Connection established. Sending filename...")
    except socket.error as e:
        print(f"\nConnection Failed: {e}")
        sys.exit(1)

    try:
        # 2. Send the filename
        client_socket.sendall(filename.encode(ENCODING))

        # 3. Receive the initial response/header
        response_header = b''
        # Read the first chunk, which should contain the header
        chunk = client_socket.recv(BUFFER_SIZE)
        if not chunk:
            print("Server closed connection without response.")
            return

        response_header = chunk.decode(ENCODING)
        
        print("\n--- Server Response ---")
        
        # Check for ERROR response
        if response_header.startswith("ERROR:"):
            print(f"Error: {response_header.split(':', 1)[1].strip()}")
        
        # Check for SUCCESS header and print content
        elif response_header.startswith("SUCCESS:"):
            parts = response_header.split(':', 1)
            if len(parts) < 2:
                 print("Invalid SUCCESS header received.")
                 return
                 
            expected_size = int(parts[1])
            print(f"File transfer initiated (Expected size: {expected_size} bytes).")
            print("File Contents:")
            print("======================================")

            # NOTE: For simplicity, the Python server sends the header and then the content immediately.
            # This logic assumes the header contains no part of the file, which is a simplification.
            # Since the header is small, the next `recv` should get the actual content.

            total_received = 0
            
            # Loop to receive the rest of the file chunks
            while True:
                data_chunk = client_socket.recv(BUFFER_SIZE)
                if not data_chunk:
                    break
                
                # We assume the content is primarily text for printing
                print(data_chunk.decode(ENCODING), end='')
                total_received += len(data_chunk)

            print("\n======================================")
            print(f"Transmission complete. Total received data: {total_received} bytes.")

        else:
            # Unexpected response, just print raw text
            print("Unexpected response received.")
            print("======================================")
            print(response_header)
            print("======================================")

    except Exception as e:
        print(f"An error occurred during communication: {e}")
    finally:
        # 4. Close the socket
        client_socket.close()

if __name__ == "__main__":
    main()
