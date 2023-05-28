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
        # Initialize the news generator.
        self.topics = ["business", "entertainment", "health", "science",
                       "sports", "technology"]
        self.events = ["new product launch", "merger", "acquisition",
                       "lawsuit", "scandal", "government regulation"]
        self.companies = ["Apple", "Microsoft", "Google", "Amazon",
                          "Facebook", "Tesla"]

    def get_news(self):
        # Generate a random news headline.
        topic = random.choice(self.topics)
        event = random.choice(self.events)
        company = random.choice(self.companies)
        headline = topic + " " + company + " " + event
        return topic, headline


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.news_generator = NewsGenerator()
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(f"tcp://*:{self.port}")

    def start(self):
        logging.info(f"Server is publishing on {self.host}:{self.port}")
        while True:
            topic, headline = self.news_generator.get_news()
            self.publisher.send_string(f"{topic} {headline}")
            time.sleep(1)


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect(f"tcp://{self.host}:{self.port}")

    def start(self):
        while True:
            topic = input("Enter topic to subscribe or 'quit' to exit: ")
            if topic == "quit":
                break
            self.subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)
            while True:
                message = self.subscriber.recv_string()
                print(f"Received: {message}")


if __name__ == "__main__":
    host = "localhost"
    port = 12345
    server = Server(host, port)
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()

    client = Client(host, port)
    client.start()
