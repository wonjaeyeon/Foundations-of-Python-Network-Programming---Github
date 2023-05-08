import socket
import ssl
import logging
import json
import zlib

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def create_client_socket(host, port, ca_cert):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=ca_cert)
    context.check_hostname = False
    tls_client_socket = context.wrap_socket(client_socket, server_hostname=host)
    tls_client_socket.connect((host, port))
    return tls_client_socket



def send_request(client_socket, task, data):
    request = {"task": task, "data": data}
    request_json = json.dumps(request)
    encrypted_request = compress_and_encrypt(request_json, client_socket)
    client_socket.sendall(encrypted_request)

def receive_response(client_socket):
    encrypted_response = client_socket.recv(4096)
    response_json = decrypt_and_decompress(encrypted_response, client_socket)
    response = json.loads(response_json)
    return response

def compress_and_encrypt(data, client_socket):
    compressed_data = zlib.compress(data.encode())
    return compressed_data

def decrypt_and_decompress(data, client_socket):
    decompressed_data = zlib.decompress(data)
    return decompressed_data.decode()

def main():
    host = "localhost"
    port = 12345
    ca_cert = "server.crt"

    while True:
        task = input("Enter task (ping, toggle_string, or quit): ")
        if task == "quit":
            break

        if task == "ping":
            domain = input("Enter the domain: ")
            client_socket = create_client_socket(host, port, ca_cert)
            send_request(client_socket, task, domain)
        elif task == "toggle_string":
            string = input("Enter the string: ")
            client_socket = create_client_socket(host, port, ca_cert)
            send_request(client_socket, task, string)
        else:
            print("Invalid task")
            continue

        response = receive_response(client_socket)
        client_socket.close()

        if "result" in response:
            print("Result: ", response["result"])
        elif "error" in response:
            print("Error: ", response["error"])

if __name__ == "__main__":
    main()
