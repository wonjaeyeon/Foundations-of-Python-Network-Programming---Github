import socket

if __name__ == '__main__':
    hostname = 'www.python.org'
    print('Address:', socket.gethostbyname(hostname))