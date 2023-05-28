import socket
import ssl
import threading
import logging
import json
import zlib

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)

            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile="server.crt", keyfile="server.key")

            logging.info(f"Server is listening on {self.host}:{self.port}")

            while True:
                conn, addr = server_socket.accept()
                client_socket = context.wrap_socket(conn, server_side=True)
                thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                thread.start()

    def handle_client(self, client_socket, client_addr):
        logging.info(f"Client connected: {client_addr}")

        try:
            data = client_socket.recv(4096)
            decrypted_data = self.decrypt_and_decompress(data)
            request = json.loads(decrypted_data)

            task = request["task"]
            task_data = request["data"]
            response = self.handle_task(task, task_data)

            response_json = json.dumps(response)
            encrypted_response = self.compress_and_encrypt(response_json)

            client_socket.sendall(encrypted_response)
        except Exception as e:
            logging.error(f"Error while handling client {client_addr}: {e}")
        finally:
            client_socket.close()
            logging.info(f"Client disconnected: {client_addr}")

    def handle_task(self, task, data):
        if task == "ping":
            return {"result": self.ping(data)}
        elif task == "toggle_string":
            return {"result": self.toggle_string(data)}
        else:
            return {"error": "Invalid task"}

    def compress_and_encrypt(self, data):
        compressed_data = zlib.compress(data.encode())
        return compressed_data

    def decrypt_and_decompress(self, data):
        decompressed_data = zlib.decompress(data)
        return decompressed_data.decode()

    def ping(self, domain):
        ip_address = socket.gethostbyname(domain)
        return ip_address

    def toggle_string(self, string):
        toggled_string = "".join(chr(ord(c) ^ 32) if 'A' <= c <= 'Z' or 'a' <= c <= 'z' else c for c in string)
        return toggled_string


class Client:
    def __init__(self, host, port, ca_cert):
        self.host = host
        self.port = port
        self.ca_cert = ca_cert

    def start(self):
        while True:
            task = input("Enter task (ping, toggle_string, or quit): ")

            if task == "quit":
                break

            if task in ["ping", "toggle_string"]:
                data = input(f"Enter the {task} data: ")
                client_socket = self.create_client_socket()
                self.send_request(client_socket, task, data)
                response = self.receive_response(client_socket)
                client_socket.close()

                if "result" in response:
                    print("Result: ", response["result"])
                elif "error" in response:
                    print("Error: ", response["error"])
            else:
                print("Invalid task")

    def create_client_socket(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=self.ca_cert)
        context.check_hostname = False
        tls_client_socket = context.wrap_socket(client_socket, server_hostname=self.host)
        tls_client_socket.connect((self.host, self.port))
        return tls_client_socket

    def send_request(self, client_socket, task, data):
        request = {"task": task, "data": data}
        request_json = json.dumps(request)
        encrypted_request = self.compress_and_encrypt(request_json)
        client_socket.sendall(encrypted_request)

    def receive_response(self, client_socket):
        encrypted_response = client_socket.recv(4096)
        response_json = self.decrypt_and_decompress(encrypted_response)
        response = json.loads(response_json)
        return response

    def compress_and_encrypt(self, data):
        compressed_data = zlib.compress(data.encode())
        return compressed_data

    def decrypt_and_decompress(self, data):
        decompressed_data = zlib.decompress(data)
        return decompressed_data.decode()


if __name__ == "__main__":
    server = Server("localhost", 12345)
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()

    client = Client("localhost", 12345, "server.crt")
    client.start()
