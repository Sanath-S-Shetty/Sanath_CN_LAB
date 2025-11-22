import socket
import os
import sys

PORT = 8080
HOST = '127.0.0.1'
BUFFER_SIZE = 1024
ENCODING = 'utf-8'

def handle_client(conn, addr):
    """Handles the file request from a single client connection."""
    print(f"Connection established with {addr[0]}:{addr[1]}")
    
    try:
        # 1. Receive filename from client
        data = conn.recv(BUFFER_SIZE)
        if not data:
            print("Client disconnected.")
            return

        filename = data.decode(ENCODING).strip()
        print(f"Client requested file: '{filename}'")

        # 2. Attempt to check and open the file
        if not os.path.exists(filename) or not os.path.isfile(filename):
            # File not found: Send error header
            error_msg = "ERROR: File Not Found."
            conn.sendall(error_msg.encode(ENCODING))
            print(f"Sent {error_msg}")
            return

        # File found:
        file_size = os.path.getsize(filename)
        print(f"File found (Size: {file_size} bytes). Sending content...")

        # Send a success header (SUCCESS:<size>)
        success_msg = f"SUCCESS:{file_size}"
        conn.sendall(success_msg.encode(ENCODING))
        
        # 3. Read and send file contents chunk by chunk
        with open(filename, 'rb') as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    # End of file
                    break
                conn.sendall(bytes_read)
        
        print("File content transmission complete.")

    except Exception as e:
        print(f"An error occurred while handling client {addr}: {e}")
    finally:
        # 4. Close the connection
        conn.close()

def main():
    """Main function to set up and run the server."""
    # Create socket file descriptor
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allows reuse of the port immediately after closing the server
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"File Server listening on {HOST}:{PORT}...")
    except socket.error as e:
        print(f"Failed to set up server: {e}")
        sys.exit(1)

    while True:
        print("\nWaiting for a new client connection...")
        try:
            # Accept new connection
            conn, addr = server_socket.accept()
            handle_client(conn, addr)
        except KeyboardInterrupt:
            print("\nServer shutting down.")
            break
        except Exception as e:
            print(f"Accept failed: {e}")
            continue

    server_socket.close()

if __name__ == "__main__":
    main()
