# 3. (4 points) Write a Python script to create a TCP Server and
# Client using the python socket standard library to develop a
# game "Guess the number.".
# The game will follow as:
# 1. The server will choose a random number between 1 to 10.
# 2. Inform the client and ask to guess a number between 1 to
# 10.
# 3. The client will send a guessed number as a request to the
# server.
# Conditions:
# 1. The client will request to start the game by sending the
# first request as "start."
# 2. The client will have only 5 attempts to guess the correct
# number
# 3. The client will only win if he guesses the correct number
# within 5 attempts and loses the game.
# The exchange of messages between the server and client during
# the game will follow the following conditions and message text
# based on the difference between the actual number with the
# server and guessed number by the client:
# x = randomly chosen number by server
# guess = number guessed by a client
# Conditions and messages:
# (x = guess) -> "Congratulations you did it."
# (x > guess) -> "You guessed too small!"
# (x < guess) -> "You Guessed too high!"

import socket
import threading
import random

def tcp_server(server_ip, server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(1)

    print("TCP server is listening...")

    while True:
        conn, client_address = server_socket.accept()
        print(f"Connected to client {client_address}")

        random_number = random.randint(1, 10)
        attempts = 5

        while attempts > 0:
            data = conn.recv(1024)
            message = data.decode('utf-8')

            if message == "start":
                conn.sendall("Guess a number between 1 and 10.".encode('utf-8'))
            else:
                try:
                    guessed_number = int(message)
                    if guessed_number == random_number:
                        conn.sendall("Congratulations you did it.".encode('utf-8'))
                        break
                    elif guessed_number > random_number:
                        conn.sendall("You guessed too high!".encode('utf-8'))
                    else:
                        conn.sendall("You guessed too small!".encode('utf-8'))
                    attempts -= 1
                except ValueError:
                    conn.sendall("Invalid input. Please guess a number between 1 and 10.".encode('utf-8'))

        if attempts == 0:
            conn.sendall("You lost the game. Better luck next time!".encode('utf-8'))

        conn.close()
        break

def tcp_client(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    client_socket.sendall("start".encode('utf-8'))

    while True:
        data = client_socket.recv(1024)
        message = data.decode('utf-8')
        print(message)

        if message.startswith("Congratulations") or message.startswith("You lost"):
            break

        guessed_number = input("Enter your guess: ")
        client_socket.sendall(guessed_number.encode('utf-8'))

    client_socket.close()

if __name__ == "__main__":
    server_ip = "127.0.0.1"
    server_port = 12345

    server_thread = threading.Thread(target=tcp_server, args=(server_ip, server_port))
    server_thread.start()

    tcp_client(server_ip, server_port)

    server_thread.join()