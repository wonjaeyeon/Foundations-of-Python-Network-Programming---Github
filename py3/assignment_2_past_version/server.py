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

            logging.info("Server is listening on {}:{}".format(self.host, self.port))

            while True:
                conn, addr = server_socket.accept()
                client_socket = context.wrap_socket(conn, server_side=True)
                thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                thread.start()

    def handle_client(self, client_socket, client_addr):
        logging.info("Client connected: {}".format(client_addr))

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
            logging.error("Error while handling client {}: {}".format(client_addr, str(e)))
        finally:
            client_socket.close()
            logging.info("Client disconnected: {}".format(client_addr))

    def handle_task(self, task, data):
        if task == "ping":
            return {"result": ping(data)}
        elif task == "toggle_string":
            return {"result": toggle_string(data)}
        else:
            return {"error": "Invalid task"}

    def compress_and_encrypt(self, data):
        compressed_data = zlib.compress(data.encode())
        return compressed_data

    def decrypt_and_decompress(self, data):
        decompressed_data = zlib.decompress(data)
        return decompressed_data.decode()

def ping(domain):
    ip_address = socket.gethostbyname(domain)
    return ip_address

def toggle_string(string):
    toggled_string = "".join(chr(ord(c) ^ 32) if 'A' <= c <= 'Z' or 'a' <= c <= 'z' else c for c in string)
    return toggled_string

if __name__ == "__main__":
    server = Server("localhost", 12345)
    server.start()
