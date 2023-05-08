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

import socket   # Import socket for network communication
import threading    # Import threading for multi-threading
import random   # Import random for random number generation

def tcp_server(server_ip, server_port):
    # Create a TCP socket using IPv4 and TCP protocol
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the server IP and port
    server_socket.bind((server_ip, server_port))
    # Listen for incoming connections
    server_socket.listen(1)

    # Print a message to the console
    print("TCP server is listening...")

    # Keep the server running in a loop
    while True:
        # Accept incoming connections
        conn, client_address = server_socket.accept()
        # Print a message to the console
        print(f"Connected to client {client_address}")

        # Generate a random number between 1 and 10
        random_number = random.randint(1, 10)
        # Set the number of variable attempts to 5
        attempts = 5

        # Keep the game running in a loop
        while attempts > 0:
            # Receive data from the client
            data = conn.recv(1024)
            # Decode the data from bytes to string
            message = data.decode('utf-8')

            # Check if the message is "start"
            if message == "start":
                conn.sendall("Guess a number between 1 and 10.".encode('utf-8'))
            # Check if the message is not "start" or a number
            else:
                # Try to convert the message to an integer
                try:
                    # Convert the message to an integer
                    guessed_number = int(message)
                    # Check if the guessed number is equal to the random number
                    if guessed_number == random_number:
                        conn.sendall("Congratulations you did it.".encode('utf-8'))
                        break
                    # Check if the guessed number is greater than the random number
                    elif guessed_number > random_number:
                        conn.sendall("You guessed too high!".encode('utf-8'))
                    # Check if the guessed number is less than the random number
                    else:
                        conn.sendall("You guessed too small!".encode('utf-8'))
                    attempts -= 1
                # If the message is not a number
                except ValueError:
                    conn.sendall("Invalid input. Please guess a number between 1 and 10.".encode('utf-8'))

        # Check if the number of attempts is 0
        if attempts == 0:
            conn.sendall("You lost the game. Better luck next time!".encode('utf-8'))

        # Close the connection
        conn.close()
        break

def tcp_client(server_ip, server_port):
    # Create a TCP socket using IPv4 and TCP protocol
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the server using the server IP and port
    client_socket.connect((server_ip, server_port))

    # Send a message to the server encoded in utf-8
    client_socket.sendall("start".encode('utf-8'))

    # Keep the game running in a loop
    while True:
        # Receive data from the server
        data = client_socket.recv(1024)
        # Decode the data from bytes to string
        message = data.decode('utf-8')
        # Print the message to the console
        print(message)

        # Check if the message is "Congratulations you did it." or "You lost the game. Better luck next time!"
        if message.startswith("Congratulations") or message.startswith("You lost"):
            break

        # Get the guessed number from the user
        guessed_number = input("Enter your guess: ")
        # Send the guessed number to the server
        client_socket.sendall(guessed_number.encode('utf-8'))

    # Close the socket
    client_socket.close()

if __name__ == "__main__":
    # Set the server IP and port
    server_ip = "127.0.0.1"
    server_port = 12345

    # Create a thread for the server
    server_thread = threading.Thread(target=tcp_server, args=(server_ip, server_port))
    # Start the server thread
    server_thread.start()

    # Call the tcp_client function
    tcp_client(server_ip, server_port)

    # Join the server thread
    server_thread.join()