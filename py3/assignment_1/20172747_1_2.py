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

import socket   # Import socket for network communication
import threading    # Import threading for multithreading
def encrypt(message):
    # Make a string variable to store the encrypted message
    encrypted = ""
    # Loop through each character in the message
    for char in message:
        # If the character is a lowercase letter, encrypt it
        if 'a' <= char <= 'z':
            encrypted += chr(((ord(char) - ord('a') + 1) % 26) + ord('a'))
        # If the character is an uppercase letter, encrypt it
        elif 'A' <= char <= 'Z':
            encrypted += chr(((ord(char) - ord('A') + 1) % 26) + ord('A'))
        # If the character is not a letter, do not encrypt it
        else:
            encrypted += char
    return encrypted

def decrypt(message):
    # Make a string variable to store the decrypted message
    decrypted = ""
    # Loop through each character in the message
    for char in message:
        # If the character is a lowercase letter, decrypt it
        if 'a' <= char <= 'z':
            decrypted += chr(((ord(char) - ord('a') - 1) % 26) + ord('a'))
        # If the character is an uppercase letter, decrypt it
        elif 'A' <= char <= 'Z':
            decrypted += chr(((ord(char) - ord('A') - 1) % 26) + ord('A'))
        # If the character is not a letter, do not decrypt it
        else:
            decrypted += char
    return decrypted



def udp_server(server_ip, server_port):
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the server IP and port
    server_socket.bind((server_ip, server_port))

    # Print a message to indicate that the server is listening
    print("UDP server is listening...")

    # Loop forever to handle incoming messages
    while True:
        # Receive a message from the client
        message, client_address = server_socket.recvfrom(1024)
        # Print the message
        print(f"Received message from {client_address}: {message.decode('utf-8')}")
        # Encrypt the message
        encrypted_message = encrypt(message.decode('utf-8'))
        # Print the encrypted message
        server_socket.sendto(encrypted_message.encode('utf-8'), client_address)

def udp_client(server_ip, server_port, message):
    # Create a UDP socket using IPv4 and UDP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Send the message to the server
    client_socket.sendto(message.encode('utf-8'), (server_ip, server_port))

    # Receive the encrypted message from the server
    encrypted_message, _ = client_socket.recvfrom(1024)
    # Decrypt the message
    decrypted_message = decrypt(encrypted_message.decode('utf-8'))
    # Print the encrypted message
    print(f"Received encrypted message: {encrypted_message.decode('utf-8')}")
    # Print the decrypted message
    print(f"Decrypted message: {decrypted_message}")

    # Close the socket
    client_socket.close()

if __name__ == "__main__":
    # Make server IP and port variables
    server_ip = "127.0.0.1"
    server_port = 12345

    # Create a thread for the server
    server_thread = threading.Thread(target=udp_server, args=(server_ip, server_port))
    # Start the server thread
    server_thread.start()

    # Create a message to send to the server
    message = "Hello, UDP Server!"
    # Call the client function
    udp_client(server_ip, server_port, message)

    # Join the server thread
    server_thread.join()