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


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.news_generator = NewsGenerator()
        self.stock_ticker = StockTicker()
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.pusher = self.context.socket(zmq.PUSH)
        self.publisher.bind(f"tcp://*:{self.port}")
        self.pusher.bind(f"tcp://*:{self.port + 1}")

    def start(self):
        logging.info(f"Server is publishing and pushing on {self.host}:{self.port}")
        while True:
            topic, headline = self.news_generator.get_news()
            self.publisher.send_string(f"{topic} {headline}")
            for company in self.stock_ticker.companies:
                price = self.stock_ticker.generate_stock_price(company)
                self.pusher.send_json({company: price})
            time.sleep(1)


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.puller = self.context.socket(zmq.PULL)
        self.subscriber.connect(f"tcp://{self.host}:{self.port}")
        self.puller.connect(f"tcp://{self.host}:{self.port + 1}")

    def start(self):
        while True:
            task = input("Enter task (subscribe or stock_ticker) or 'quit' to exit: ")
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



if __name__ == "__main__":
    host = "localhost"
    port = 12345
    server = Server(host, port)
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()

    client = Client(host, port)
    client.start()
