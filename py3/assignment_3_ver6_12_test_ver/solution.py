import zmq
import time
import threading
import json
import random

class Server:
    def __init__(self):
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.bind("tcp://*:5556")

        self.rep_socket = self.context.socket(zmq.REP)
        self.rep_socket.bind("tcp://*:5555")

        self.chatrooms = {}

    def handle_messages(self):
        while True:
            message = self.rep_socket.recv_json()
            chatroom = message['chatroom']
            if chatroom not in self.chatrooms:
                self.chatrooms[chatroom] = []
            self.chatrooms[chatroom].append(message['message'])
            self.rep_socket.send_json({"status": "message received"})
            self.pub_socket.send_string(f"{chatroom} {message['message']}")

    def start(self):
        threading.Thread(target=self.handle_messages, daemon=True).start()
        while True:
            time.sleep(1)


class Client:
    def __init__(self, username, chatroom):
        self.context = zmq.Context()

        self.pub_socket = self.context.socket(zmq.SUB)
        self.pub_socket.connect("tcp://localhost:5556")
        self.pub_socket.setsockopt_string(zmq.SUBSCRIBE, chatroom)

        self.req_socket = self.context.socket(zmq.REQ)
        self.req_socket.connect("tcp://localhost:5555")

        self.username = username
        self.chatroom = chatroom

    def send_message(self, message):
        self.req_socket.send_json({"chatroom": self.chatroom, "message": f"{self.username}: {message}"})
        print(self.req_socket.recv_json()['status'])

    def receive_messages(self):
        while True:
            message = self.pub_socket.recv_string()
            print(message)

    def start(self):
        threading.Thread(target=self.receive_messages, daemon=True).start()
        while True:
            message = input(f"{self.username}: ")
            self.send_message(message)


if __name__ == "__main__":
    choice = input("Do you want to start a server or client? (server/client): ")
    if choice.lower() == "server":
        server = Server()
        server.start()
    elif choice.lower() == "client":
        username = input("Enter a username: ")
        chatroom = input("Enter a chatroom: ")
        client = Client(username, chatroom)
        client.start()
