import socket
import ssl
import threading
import logging
import json
import zlib
import zmq
import random

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
# def main():
#     host = "localhost"
#     port = 5555
#     ca_cert = "server.crt"
#
#     print()
#
#     # Main loop for handling user input and interacting with the server
#     while True:
#         # Prompt the user for the task to perform
#         task = input("Enter task (ping, toggle_string, or quit): ")
#
#         # Exit the loop if the user enters "quit"
#         if task == "quit":
#             break
#
#         # If the user enters "ping", prompt for a domain and send the request to the server
#         if task == "ping":
#             # Prompt the user for the domain to ping
#             domain = input("Enter the domain: ")
#             client_socket = create_client_socket(host, port, ca_cert)
#             send_request(client_socket, task, domain)
#
#         # If the user enters "toggle_string", prompt for a string and send the request to the server
#         elif task == "toggle_string":
#             # Prompt the user for the string to toggle
#             string = input("Enter the string: ")
#             client_socket = create_client_socket(host, port, ca_cert)
#             send_request(client_socket, task, string)
#
#         # If the user enters an invalid task, print an error message and continue
#         else:
#             print("Invalid task")
#             continue
#
#         # Receive the response from the server and close the client socket
#         response = receive_response(client_socket)
#         client_socket.close()
#
#         # Print the result or error message from the server response
#         if "result" in response:
#             print("Result: ", response["result"])
#         elif "error" in response:
#             print("Error: ", response["error"])

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.news_generator = NewsGenerator()
        self.stock_ticker = StockTicker()
        self.chatroom = Chatroom()

    def start(self):
        # ZeroMQ Context
        context = zmq.Context()

        # Define the socket using the "Context"
        sock = context.socket(zmq.REP)
        sock.bind("tcp://*:{}".format(self.port))


        while True:
            # Wait for next request from client
            message = sock.recv()
            print("Received request: %s" % message)
            message = message.decode()
            task, data = message.split()

            if task == 'ping':
                sock.send_string("pong")
            elif task == 'subscribe':
                sock.send_string(self.news_generator.get_news())
            elif task == 'stock_ticker':
                sock.send_string(str(self.stock_ticker.generate_stock_price(data)))
            elif task == 'chat':
                sock.send_string(self.chatroom.join(data))
            else:
                sock.send(b"unknown task")


class NewsGenerator:
    def __init__(self):
        self.topics = ["business", "entertainment", "health", "science", "sports", "technology"]
        self.events = ["new product launch", "merger", "acquisition", "lawsuit", "scandal", "government regulation"]
        self.companies = ["Apple", "Microsoft", "Google", "Amazon", "Facebook", "Tesla"]

    def get_news(self):
        topic = random.choice(self.topics)
        event = random.choice(self.events)
        company = random.choice(self.companies)
        headline = topic + " " + company + " " + event
        return headline


class StockTicker:
    def __init__(self):
        self.companies = ["AAPL", "MSFT", "GOOGL"]
        self.prices = {}
        for company in self.companies:
            self.prices[company] = random.randint(100, 1000)

    def generate_stock_price(self, company):
        if company not in self.companies:
            raise ValueError("Invalid company")
        price = random.randint(100, 1000)
        self.prices[company] = price
        return price


class Chatroom:
    def __init__(self):
        self.clients = []

    def join(self, client):
        self.clients.append(client)
        return "Joined chatroom"

    def leave(self, client):
        self.clients.remove(client)

    def send(self, sender, message):
        for client in self.clients:
            if client != sender:
                client.send((sender, message))

# Function to resolve a domain to its IP address using the socket library
def ping(domain):
    ip_address = socket.gethostbyname(domain)
    return ip_address

# Function to convert a character to a number
def custom_ord(char):
    return int.from_bytes(char.encode(), 'little')

# Function to convert a number to a character
def custom_chr(number):
    return (number).to_bytes((number.bit_length() + 7) // 8, 'little').decode()

# Function to toggle the case of alphabetic characters in a string
def toggle_string(string):
    toggled_string = "".join(custom_chr(custom_ord(c) ^ 32) if 'A' <= c <= 'Z' or 'a' <= c <= 'z' else c for c in string)
    return toggled_string


class Client:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port

    def send_request(self, task, data=''):
        context = zmq.Context()
        print("Connecting to server...")
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://{}:{}".format(self.server_host, self.server_port))

        print("Sending request ", task, data)
        socket.send_string(task + ' ' + data)

        # Get the reply.
        message = socket.recv()
        print("Received reply: ", message)

# Main entry point for the application
if __name__ == "__main__":
    # Create a server object and start it in a separate daemon thread
    server = Server("localhost", 5555)
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True  # Set the server thread to exit when the main thread exits
    server_thread.start()

    client = Client("localhost", 5555)
    while True:
        task = input("Enter task (ping, subscribe, stock_ticker, chat): ")
        if task not in ['ping', 'subscribe', 'stock_ticker', 'chat']:
            print("Invalid task. Please enter a valid task.")
            continue
        data = ''
        if task == 'ping':
            data = input("Enter domain name: ")
        if task == 'subscribe':
            data = input("Enter topic (business, entertainment, health, science, sports, technology): ")
        if task == 'stock_ticker':
            data = input("Enter company name (AAPL, MSFT, GOOGL): ")
        elif task == 'chat':
            data = input("Enter chatroom name: ")
        client.send_request(task, data)