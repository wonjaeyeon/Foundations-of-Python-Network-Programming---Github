import socket
import ssl
import threading
import logging
import json
import zlib
import random
import time
import zmq

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class NewsGenerator:
    def __init__(self):
        self.topics = ["business", "entertainment", "health", "science",
                       "sports", "technology"]
        self.events = ["new product launch", "merger", "acquisition",
                       "lawsuit", "scandal", "government regulation"]
        self.companies = ["Apple", "Microsoft", "Google", "Amazon",
                          "Facebook", "Tesla"]

    def get_news(self):
        topic = random.choice(self.topics)
        event = random.choice(self.events)
        company = random.choice(self.companies)
        headline = topic + " " + company + " " + event
        return topic, headline


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
    def leave(self, client):
        self.clients.remove(client)
    def send(self, sender, message):
        for client in self.clients:
            if client != sender:
                client.send((sender, message))

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.news_generator = NewsGenerator()
        self.stock_ticker = StockTicker()
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.pusher = self.context.socket(zmq.PUSH)
        self.responder = self.context.socket(zmq.REP)  # new REQ-REP socket for chat
        self.publisher.bind(f"tcp://*:{self.port}")
        self.pusher.bind(f"tcp://*:{self.port + 1}")
        self.responder.bind(f"tcp://*:{self.port + 2}")  # bind to a new port
        self.chatrooms = {}  # chatrooms dictionary

    def start(self):
        logging.info(f"Server is publishing and pushing on {self.host}:{self.port}")
        while True:
            topic, headline = self.news_generator.get_news()
            self.publisher.send_string(f"{topic} {headline}")
            for company in self.stock_ticker.companies:
                price = self.stock_ticker.generate_stock_price(company)
                self.pusher.send_json({company: price})

            if self.responder.poll(1000):  # check if there is a chat request
                request = json.loads(self.responder.recv_string())
                action = request.get("action")
                chatroom = request.get("chatroom")
                message = request.get("message")
                if action == 'join':
                    if chatroom not in self.chatrooms:
                        self.chatrooms[chatroom] = []
                    self.chatrooms[chatroom].append(message)
                elif action == 'leave':
                    self.chatrooms[chatroom].remove(message)
                elif action == 'send':
                    self.chatrooms[chatroom].append(message)
                self.responder.send_string(json.dumps(self.chatrooms[chatroom]))
            time.sleep(1)


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.puller = self.context.socket(zmq.PULL)
        self.requester = self.context.socket(zmq.REQ)  # new REQ-REP socket for chat
        self.subscriber.connect(f"tcp://{self.host}:{self.port}")
        self.puller.connect(f"tcp://{self.host}:{self.port + 1}")
        self.requester.connect(f"tcp://{self.host}:{self.port + 2}")  # connect to the new port

    def start(self):
        while True:
            task = input("Enter task (subscribe, stock_ticker, or chat) or 'quit' to exit: ")
            if task == "quit":
                break
            elif task == "subscribe":
                topic = input("Enter topic to subscribe: ")
                self.subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)
                message = self.subscriber.recv_string()
                print(f"Received: {message}")
            elif task == "stock_ticker":
                company = input("Enter company to get stock price: ")
                message = self.puller.recv_json()
                if company in message:
                    print(f"Received: {company} stock price is {message[company]}")
            elif task == "chat":
                action = input("Enter action (join, leave, send): ")
                chatroom = input("Enter chatroom: ")
                message = None
                if action == "send":
                    message = input("Enter message: ")
                self.requester.send_string(json.dumps({"action": action, "chatroom": chatroom, "message": message}))
                print(self.requester.recv_string())

if __name__ == "__main__":
    host = "localhost"
    port = 12345
    server = Server(host, port)
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()

    client = Client(host, port)
    client.start()
