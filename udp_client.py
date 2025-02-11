import socket
import hashlib  # needed to calculate the SHA256 hash of the file
import sys  # needed to get cmd line parameters
import os.path as path  # needed to get size of file in bytes


IP = '127.0.0.1'  # change to the IP address of the server
PORT = 12000  # change to a desired port number
BUFFER_SIZE = 1024  # change to a desired buffer size


def get_file_size(file_name: str) -> int:
    size = 0
    try:
        size = path.getsize(file_name)
    except FileNotFoundError as fnfe:
        print(fnfe)
        sys.exit(1)
    return size


def send_file(filename: str):
    
    # get the file size in bytes
    # TODO: section 2 step 2 in README.md file
    fileSize = get_file_size(filename)
    
    # convert the file size to an 8-byte byte string using big endian
    # TODO: section 2 step 3 in README.md file
    fileToByte = fileSize.to_bytes(8, byteorder='big')

    # create a SHA256 object to generate hash of file
    # TODO: section 2 step 4 in README.md file
    sha = hashlib.sha256()

    # create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending file size: {fileToByte}")
    print(f"Sending file name: {filename.encode()}")

    try:
        # send the file size in the first 8-bytes followed by the bytes
        # for the file name to server at (IP, PORT)
        # TODO: section 2 step 6 in README.md file
        # + '.temp'.encode()
        client_socket.sendto(fileToByte + filename.encode(), (IP, PORT))

        # TODO: section 2 step 7 in README.md file
        response, addr = client_socket.recvfrom(BUFFER_SIZE)
        if response != b'go ahead':
            raise Exception('Bad server response - was not go ahead!')

        # open the file to be transferred
        with open(file_name, 'rb') as file:
            while True:
            # read the file in chunks and send each chunk to the server
            # TODO: section 2 step 8 a-d in README.md file
                chunk = file.read(BUFFER_SIZE)
                if len(chunk) > 0:
                        sha.update(chunk)
                        client_socket.sendto(chunk, (IP, PORT))
                        ack, addr = client_socket.recvfrom(BUFFER_SIZE)
                        if ack != b'received':
                            raise Exception('Bad server response - was not received')
                else:
                    break

                pass  # replace this line with your code

        # send the hash value so server can verify that the file was
        # received correctly.
        # TODO: section 2 step 9 in README.md file
        client_socket.sendto(sha.digest(), (IP, PORT))

        # TODO: section 2 steps 10 in README.md file
        result, addr = client_socket.recvfrom(BUFFER_SIZE)

        # TODO: section 2 step 11 in README.md file
        if result == b'success':
            print('Transfer completed!')
        else:
            raise Exception('Transfer failed!')
    except Exception as e:
        print(f'An error occurred while sending the file: {e}')
    finally:
        client_socket.close()


if __name__ == '__main__':
    # get filename from cmd line
    if len(sys.argv) < 2:
        print(f'SYNOPSIS: {sys.argv[0]} <filename>')
        sys.exit(1)
    file_name = sys.argv[1]  # filename from cmdline argument
    send_file(file_name)
    
