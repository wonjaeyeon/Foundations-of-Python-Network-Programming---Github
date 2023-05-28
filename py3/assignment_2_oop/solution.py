import socket
import ssl
import threading
import logging
import json
import zlib

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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

class Client:
    def __init__(self, host, port, ca_cert):
        self.host = host
        self.port = port
        self.ca_cert = ca_cert

    def create_client_socket(self):
        # Create a new socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set up SSL/TLS context with the CA certificate
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=self.ca_cert)
        context.check_hostname = False

        # Wrap the socket with SSL/TLS
        tls_client_socket = context.wrap_socket(client_socket, server_hostname=self.host)

        # Connect to the server
        tls_client_socket.connect((self.host, self.port))
        return tls_client_socket

    def send_request(self, client_socket, task, data):
        # Create a request dictionary
        request = {"task": task, "data": data}

        # Convert the dictionary to a JSON string
        request_json = json.dumps(request)

        # Compress and encrypt the JSON string
        encrypted_request = self.compress_and_encrypt(request_json, client_socket)

        # Send the encrypted request to the server
        client_socket.sendall(encrypted_request)

    def receive_response(self, client_socket):
        # Initialize a buffer to hold the received data
        buffer = b""

        # Keep receiving data until we get a complete message
        while True:
            # Receive some data from the server
            data = client_socket.recv(4096)

            # Add the received data to the buffer
            buffer += data

            # If we didn't receive any data, or if we received less than the maximum amount,
            # then we've received all the data
            if not data or len(data) < 4096:
                break

        # Decrypt and decompress the buffered data
        response_json = self.decrypt_and_decompress(buffer, client_socket)

        # Convert the JSON string to a dictionary
        response = json.loads(response_json)
        return response

    def compress_and_encrypt(self, data, client_socket):
        # Compress the data using zlib
        compressed_data = zlib.compress(data.encode())
        return compressed_data

    def decrypt_and_decompress(self, data, client_socket):
        # Decompress the data using zlib
        decompressed_data = zlib.decompress(data)
        return decompressed_data.decode()

    def start(self):
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
                client_socket = self.create_client_socket()
                self.send_request(client_socket, task, domain)

            # If the user enters "toggle_string", prompt for a string and send the request to the server
            elif task == "toggle_string":
                # Prompt the user for the string to toggle
                string = input("Enter the string: ")
                client_socket = self.create_client_socket()
                self.send_request(client_socket, task, string)

            # If the user enters an invalid task, print an error message and continue
            else:
                print("Invalid task")
                continue

            # Receive the response from the server and close the client socket
            response = self.receive_response(client_socket)
            client_socket.close()

            # Print the result or error message from the server response
            if "result" in response:
                print("Result: ", response["result"])
            elif "error" in response:
                print("Error: ", response["error"])


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)

            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile="ssu.crt", keyfile="ssu.key")

            logging.info("Server is listening on {}:{}".format(self.host, self.port))

            while True:
                conn, addr = server_socket.accept()
                client_socket = context.wrap_socket(conn, server_side=True)
                thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                thread.start()

    def handle_client(self, client_socket, client_addr):
        logging.info("Client connected: {}".format(client_addr))

        try:
            data = client_socket.recv(4096)

            decrypted_data = self.decrypt_and_decompress(data)

            request = json.loads(decrypted_data)

            task = request["task"]
            task_data = request["data"]
            response = self.handle_task(task, task_data)

            response_json = json.dumps(response)

            encrypted_response = self.compress_and_encrypt(response_json)

            client_socket.sendall(encrypted_response)

        except Exception as e:
            logging.error("Error while handling client {}: {}".format(client_addr, str(e)))

        finally:
            client_socket.close()
            logging.info("Client disconnected: {}".format(client_addr))

    def handle_task(self, task, data):
        if task == "ping":
            return {"result": ping(data)}
        elif task == "toggle_string":
            return {"result": toggle_string(data)}
        else:
            return {"error": "Invalid task"}

    def compress_and_encrypt(self, data):
        compressed_data = zlib.compress(data.encode())
        return compressed_data

    def decrypt_and_decompress(self, data):
        decompressed_data = zlib.decompress(data)
        return decompressed_data.decode()

# Add your ping and toggle_string functions here

if __name__ == "__main__":
    server = Server("localhost", 12345)
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()

    client = Client("localhost", 12345, "ssu.crt")
    client.start()
