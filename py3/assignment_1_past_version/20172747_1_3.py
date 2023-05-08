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
import random
import threading

def tcp_server(server_ip, server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(1)

    print("TCP server is listening...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

def handle_client(client_socket):
    number = random.randint(1, 10)
    attempts = 5

    client_socket.sendall(b"Guess a number between 1 to 10\n")

    while attempts > 0:
        guess = int(client_socket.recv(1024).decode().strip())

        if guess == number:
            client_socket.sendall(b"Congratulations you did it.\n")
            break
        elif guess < number:
            response = "You guessed too small! "
        else:
            response = "You guessed too high! "
        attempts -= 1

        if attempts > 0:
            response += f"Remaining attempts: {attempts}\n"
        else:
            response += "No more attempts. You lost the game.\n"

        client_socket.sendall(response.encode())

    client_socket.close()

def tcp_client(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    client_socket.sendall(b"start")

    while True:
        message = client_socket.recv(1024)
        if not message:
            break

        print(message.decode(), end="")
        guess = input("Your guess: ")
        client_socket.sendall(guess.encode())

    client_socket.close()

if __name__ == "__main__":
    server_ip = "127.0.0.1"
    server_port = 12345

    server_thread = threading.Thread(target=tcp_server, args=(server_ip, server_port))
    server_thread.start()

    tcp_client(server_ip, server_port)

    server_thread.join()