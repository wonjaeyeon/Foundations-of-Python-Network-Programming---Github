import socket
import ssl
import threading
import logging
import json
import zlib
import time

import zmq
import random


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

class Server:
    def __init__(self):
        self.context = zmq.Context()
        self.news_generator = NewsGenerator()
        self.stock_ticker = StockTicker()
        self.chatroom = Chatroom()
        self.clients = []

        self.pub_sub_socket = self.context.socket(zmq.PUB)
        self.push_pull_socket = self.context.socket(zmq.PUSH)
        self.req_rep_socket = self.context.socket(zmq.REP)

    def start(self):
        self.pub_sub_socket.bind("tcp://*:5555")
        self.push_pull_socket.bind("tcp://*:5556")
        self.req_rep_socket.bind("tcp://*:5557")

        threading.Thread(target=self.pub_sub_service).start()
        threading.Thread(target=self.push_pull_service).start()
        threading.Thread(target=self.req_rep_service).start()

    def pub_sub_service(self):
        while True:
            headline = self.news_generator.get_news()
            self.pub_sub_socket.send_string(headline)

    def push_pull_service(self):
        while True:
            for company in self.stock_ticker.companies:
                price = self.stock_ticker.generate_stock_price(company)
                self.push_pull_socket.send_string(f"{company} {price}")

    def req_rep_service(self):
        while True:
            client_msg = self.req_rep_socket.recv_string()
            client, chatroom_name, message = client_msg.split()
            if client not in self.clients:
                self.clients.append(client)
                self.chatroom.join(client)
            self.chatroom.send(client, message)
class Client:
    def __init__(self, client_id):
        self.context = zmq.Context()
        self.client_id = client_id

        self.pub_sub_socket = self.context.socket(zmq.SUB)
        self.pull_socket = self.context.socket(zmq.PULL)
        self.req_socket = self.context.socket(zmq.REQ)

    def start(self):
        self.pub_sub_socket.connect("tcp://localhost:5555")
        self.pull_socket.connect("tcp://localhost:5556")
        self.req_socket.connect("tcp://localhost:5557")

        self.pub_sub_socket.setsockopt_string(zmq.SUBSCRIBE, '')

        threading.Thread(target=self.subscribe_to_news).start()
        threading.Thread(target=self.pull_stock_prices).start()
        threading.Thread(target=self.join_chat).start()

    def subscribe_to_news(self):
        while True:
            message = self.pub_sub_socket.recv_string()
            print(f"Client {self.client_id} received news: {message}")

    def pull_stock_prices(self):
        while True:
            message = self.pull_socket.recv_string()
            print(f"Client {self.client_id} received stock price: {message}")

    def join_chat(self):
        while True:
            self.req_socket.send_string(f"{self.client_id} chatroom1 Hello")
            message = self.req_socket.recv_string()
            print(f"Client {self.client_id} received chat message: {message}")



if __name__ == "__main__":
    # Create a server object and start it in a separate daemon thread
    server = Server()
    server.start()

    time.sleep(1)  # Ensure server starts before client

    client1 = Client('client1')
    client1.start()

    client2 = Client('client2')
    client2.start()