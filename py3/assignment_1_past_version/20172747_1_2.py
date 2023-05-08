# 2. (3 points) Write a python script to create a UDP Server and
# Client using the python socket standard library where the
# client sends a message to the server and the server replies to
# the message. However, there's a twist: the reply from the
# server must be encrypted using a custom encryption algorithm
# that you've developed.
# Algorithm:
# The encryption algorithm works as follows: each character
# in the message is replaced with the ASCII code for the
# next character in the English alphabet. For example, 'a'
# is replaced with 'b', 'b' is replaced with 'c', and so
# on. The last character in the alphabet, 'z', is replaced
# with 'a'. The resulting encrypted message is then sent
# over the UDP connection.
import socket
def encrypt(message):
    encrypted = ""
    for char in message:
        if 'a' <= char <= 'z':
            encrypted += chr(((ord(char) - ord('a') + 1) % 26) + ord('a'))
        elif 'A' <= char <= 'Z':
            encrypted += chr(((ord(char) - ord('A') + 1) % 26) + ord('A'))
        else:
            encrypted += char
    return encrypted

def decrypt(message):
    decrypted = ""
    for char in message:
        if 'a' <= char <= 'z':
            decrypted += chr(((ord(char) - ord('a') - 1) % 26) + ord('a'))
        elif 'A' <= char <= 'Z':
            decrypted += chr(((ord(char) - ord('A') - 1) % 26) + ord('A'))
        else:
            decrypted += char
    return decrypted



def udp_server(server_ip, server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((server_ip, server_port))

    print("UDP server is listening...")

    while True:
        message, client_address = server_socket.recvfrom(1024)
        print(f"Received message from {client_address}: {message.decode('utf-8')}")
        encrypted_message = encrypt(message.decode('utf-8'))
        server_socket.sendto(encrypted_message.encode('utf-8'), client_address)

def udp_client(server_ip, server_port, message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(message.encode('utf-8'), (server_ip, server_port))

    encrypted_message, _ = client_socket.recvfrom(1024)
    decrypted_message = decrypt(encrypted_message.decode('utf-8'))
    print(f"Received encrypted message: {encrypted_message.decode('utf-8')}")
    print(f"Decrypted message: {decrypted_message}")

    client_socket.close()

if __name__ == "__main__":
    import threading

    server_ip = "127.0.0.1"
    server_port = 12345

    server_thread = threading.Thread(target=udp_server, args=(server_ip, server_port))
    server_thread.start()

    message = "Hello, UDP Server!"
    udp_client(server_ip, server_port, message)

    server_thread.join()