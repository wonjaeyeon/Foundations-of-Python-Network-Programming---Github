import socket
import ssl
import threading
import logging
import json
import zlib
import zmq
import random

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.context = zmq.Context()

        # Socket to receive messages on
        self.receiver = self.context.socket(zmq.ROUTER)
        self.receiver.bind(f'tcp://*:{self.port}')

        # Socket to send messages to
        self.sender = self.context.socket(zmq.PUB)
        self.sender.bind(f'tcp://*:{self.port + 1}')

    def start(self):
        while True:
            # Wait for next request from client
            sender_id, message = self.receiver.recv_multipart()
            print(f'Received request: {message} from {sender_id}')
            message = message.decode()

            # send the message to all clients
            self.sender.send_string(message)


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

class Client:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.SUB)
        self.receiver.connect(f'tcp://{self.server_host}:{self.server_port + 1}')
        self.receiver.setsockopt_string(zmq.SUBSCRIBE, '')

        self.sender = self.context.socket(zmq.DEALER)
        self.sender.connect(f'tcp://{self.server_host}:{self.server_port}')

    def send_message(self, message):
        self.sender.send_string(message)

    def receive_message(self):
        while True:
            message = self.receiver.recv_string()
            print(f'Received message: {message}')

if __name__ == "__main__":
    # Create a server object and start it in a separate daemon thread
    server = Server('localhost', 5555)
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True  # Set the server thread to exit when the main thread exits
    server_thread.start()

    client1 = Client('localhost', 5555)
    client1_thread = threading.Thread(target=client1.receive_message)
    client1_thread.daemon = True
    client1_thread.start()

    client2 = Client('localhost', 5555)
    client2_thread = threading.Thread(target=client2.receive_message)
    client2_thread.daemon = True
    client2_thread.start()

    while True:
        message = input('Enter message: ')
        client1.send_message(message)