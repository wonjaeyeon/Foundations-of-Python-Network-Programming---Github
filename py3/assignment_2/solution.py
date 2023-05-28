import socket
import ssl
import threading
import logging
import json
import zlib

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Function to create a secure client socket connection using SSL/TLS
def create_client_socket(host, port, ca_cert):
    # Create a new socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set up SSL/TLS context with the CA certificate
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=ca_cert)
    context.check_hostname = False

    # Wrap the socket with SSL/TLS
    tls_client_socket = context.wrap_socket(client_socket, server_hostname=host)

    # Connect to the server
    tls_client_socket.connect((host, port))
    return tls_client_socket


# Function to send a request to the server using the secure client socket
def send_request(client_socket, task, data):
    # Create a request dictionary
    request = {"task": task, "data": data}

    # Convert the dictionary to a JSON string
    request_json = json.dumps(request)

    # Compress and encrypt the JSON string
    encrypted_request = compress_and_encrypt(request_json, client_socket)

    # Send the encrypted request to the server
    client_socket.sendall(encrypted_request)


# Function to receive a response from the server using the secure client socket
def receive_response(client_socket):
    # Receive the encrypted response from the server
    encrypted_response = client_socket.recv(4096)

    # Decrypt and decompress the encrypted response
    response_json = decrypt_and_decompress(encrypted_response, client_socket)

    # Convert the JSON string to a dictionary
    response = json.loads(response_json)
    return response


# Function to compress and encrypt data using zlib
def compress_and_encrypt(data, client_socket):
    # Compress the data using zlib
    compressed_data = zlib.compress(data.encode())
    return compressed_data


# Function to decrypt and decompress data using zlib
def decrypt_and_decompress(data, client_socket):
    # Decompress the data using zlib
    decompressed_data = zlib.decompress(data)
    return decompressed_data.decode()


# Main function for the client-side of the application
def main():
    host = "localhost"
    port = 12345
    ca_cert = "server.crt"

    print()

    # Main loop for handling user input and interacting with the server
    while True:
        # Prompt the user for the task to perform
        task = input("Enter task (ping, toggle_string, or quit): ")

        # Exit the loop if the user enters "quit"
        if task == "quit":
            break

        # If the user enters "ping", prompt for a domain and send the request to the server
        if task == "ping":
            # Prompt the user for the domain to ping
            domain = input("Enter the domain: ")
            client_socket = create_client_socket(host, port, ca_cert)
            send_request(client_socket, task, domain)

        # If the user enters "toggle_string", prompt for a string and send the request to the server
        elif task == "toggle_string":
            # Prompt the user for the string to toggle
            string = input("Enter the string: ")
            client_socket = create_client_socket(host, port, ca_cert)
            send_request(client_socket, task, string)

        # If the user enters an invalid task, print an error message and continue
        else:
            print("Invalid task")
            continue

        # Receive the response from the server and close the client socket
        response = receive_response(client_socket)
        client_socket.close()

        # Print the result or error message from the server response
        if "result" in response:
            print("Result: ", response["result"])
        elif "error" in response:
            print("Error: ", response["error"])

# Server class to handle incoming connections and process requests
class Server:
    # Constructor to initialize the Server object with the host and port
    def __init__(self, host, port):
        self.host = host
        self.port = port

    # Function to start the server and listen for incoming connections
    def start(self):
        # Create a new socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)

            # Set up SSL/TLS context with the server certificate and private key
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile="server.crt", keyfile="server.key")

            # Log that the server is listening
            logging.info("Server is listening on {}:{}".format(self.host, self.port))

            # Accept incoming connections and handle them in separate threads
            while True:
                conn, addr = server_socket.accept()
                client_socket = context.wrap_socket(conn, server_side=True)
                thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                thread.start()

    # Function to handle each client connection in a separate thread
    def handle_client(self, client_socket, client_addr):
        logging.info("Client connected: {}".format(client_addr))

        try:
            # Receive the encrypted and compressed data from the client
            data = client_socket.recv(4096)

            # Decrypt and decompress the received data
            decrypted_data = self.decrypt_and_decompress(data)

            # Convert the decrypted JSON string to a dictionary
            request = json.loads(decrypted_data)

            # Process the task requested by the client
            task = request["task"]
            task_data = request["data"]
            response = self.handle_task(task, task_data)

            # Convert the response dictionary to a JSON string
            response_json = json.dumps(response)

            # Compress and encrypt the JSON string
            encrypted_response = self.compress_and_encrypt(response_json)

            # Send the encrypted response to the client
            client_socket.sendall(encrypted_response)

        except Exception as e:
            # Log the error
            logging.error("Error while handling client {}: {}".format(client_addr, str(e)))

        finally:
            # Close the client socket and log the disconnection
            client_socket.close()
            logging.info("Client disconnected: {}".format(client_addr))

    # Function to process a task requested by the client
    def handle_task(self, task, data):
        if task == "ping":
            return {"result": ping(data)}
        elif task == "toggle_string":
            return {"result": toggle_string(data)}
        else:
            return {"error": "Invalid task"}

    # Function to compress and encrypt data using zlib
    def compress_and_encrypt(self, data):
        compressed_data = zlib.compress(data.encode())
        return compressed_data

    # Function to decrypt and decompress data using zlib
    def decrypt_and_decompress(self, data):
        decompressed_data = zlib.decompress(data)
        return decompressed_data.decode()

# Function to resolve a domain to its IP address using the socket library
def ping(domain):
    ip_address = socket.gethostbyname(domain)
    return ip_address

def custom_ord(char):
    return int.from_bytes(char.encode(), 'little')

def custom_chr(number):
    return (number).to_bytes((number.bit_length() + 7) // 8, 'little').decode()


# Function to toggle the case of alphabetic characters in a string
# def toggle_string(string):
#     toggled_string = "".join(chr(ord(c) ^ 32) if 'A' <= c <= 'Z' or 'a' <= c <= 'z' else c for c in string)
#     return toggled_string

def toggle_string(string):
    toggled_string = "".join(custom_chr(custom_ord(c) ^ 32) if 'A' <= c <= 'Z' or 'a' <= c <= 'z' else c for c in string)
    return toggled_string


# Main entry point for the application
if __name__ == "__main__":
    # Create a server object and start it in a separate daemon thread
    server = Server("localhost", 12345)
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True  # Set the server thread to exit when the main thread exits
    server_thread.start()

    # Run the main client-side loop
    main()