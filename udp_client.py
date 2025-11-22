import socket
import sys

PORT = 8080
HOST = '127.0.0.1'
BUFFER_SIZE = 1500 # Slightly larger than the expected max packet size (CHUNK_SIZE + headers)
ENCODING = 'utf-8'

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Dictionary to store received chunks {seq_num: data_bytes}
    received_chunks = {}
    last_seq_num = 0

    print(f"Attempting to request file: '{filename}' from {HOST}:{PORT}")

    # 1. Create UDP socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set a timeout for receiving data (UDP is unreliable, so we don't wait forever)
        client_socket.settimeout(5.0) 
    except socket.error as e:
        print(f"\nSocket creation error: {e}")
        sys.exit(1)

    try:
        server_address = (HOST, PORT)
        
        # 2. Send the filename request
        client_socket.sendto(filename.encode(ENCODING), server_address)
        print("Filename sent. Waiting for file chunks...")

        # 3. Receive chunks
        while True:
            try:
                data, server = client_socket.recvfrom(BUFFER_SIZE)
                
                # Check for ERROR response (no sequence number)
                if data.decode(ENCODING).startswith("ERROR:"):
                    print("\n--- Server Response ---")
                    print(f"Error: {data.decode(ENCODING).split(':', 1)[1].strip()}")
                    return
                
                # Split packet into header and payload
                header_end = data.find(b':')
                if header_end == -1:
                    print(f"Warning: Received malformed packet. Skipping.")
                    continue

                seq_num_str = data[:header_end].decode(ENCODING)
                payload = data[header_end + 1:]
                
                try:
                    seq_num = int(seq_num_str)
                except ValueError:
                    print(f"Warning: Invalid sequence number '{seq_num_str}'. Skipping.")
                    continue
                
                # Check for completion marker
                if payload.decode(ENCODING).strip() == "FILE_TRANSFER_COMPLETE":
                    last_seq_num = seq_num - 1 # The sequence number of the last data packet
                    print(f"Received completion marker. Total data packets expected: {last_seq_num}")
                    break

                # Store the chunk
                if seq_num not in received_chunks:
                    received_chunks[seq_num] = payload
                
            except socket.timeout:
                print("Socket timeout reached. Assuming transmission complete or lost packets.")
                # We break here because UDP doesn't guarantee delivery; we take what we got.
                break
        
        # 4. Reassemble and Print Content
        print("\n--- Reassembly & Output ---")
        if not received_chunks:
            print("No data received or file was empty.")
            return

        # Sort chunks by sequence number
        sorted_keys = sorted(received_chunks.keys())
        total_received_bytes = 0

        print("File Contents:")
        print("======================================")
        
        # Concatenate and print (assuming text content)
        for seq_num in sorted_keys:
            chunk = received_chunks[seq_num]
            print(chunk.decode(ENCODING), end='')
            total_received_bytes += len(chunk)

        # Check for missing packets (for debugging/diagnostic)
        missing_packets = set(range(1, last_seq_num + 1)) - set(received_chunks.keys())
        if missing_packets:
            print(f"\n\nWARNING: Missing packets detected: {len(missing_packets)} packet(s).")
            # print(f"Missing sequence numbers: {sorted(list(missing_packets))}") # Uncomment for verbose error
        
        print("\n======================================")
        print(f"Transmission complete. Total received data: {total_received_bytes} bytes.")
        

    except Exception as e:
        print(f"An error occurred during communication: {e}")
    finally:
        # 5. Close the socket
        client_socket.close()

if __name__ == "__main__":
    main()
