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

    def aaa(self):
        pass


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
