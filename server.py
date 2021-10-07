import time
import socket
import threading


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.members = []

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen(0)
        threading.Thread(target=self.connect).start()
        print(f'Listening at {self.ip}:{self.port}')

    def connect(self):
        while True:
            client, address = self.server.accept()
            if client not in self.members:
                self.members.append(client)
                threading.Thread(target=self.message_handler, args=(client,)).start()
                client.send('Успешное подключение к чату!'.encode('utf-8'))
            time.sleep(1)

    def message_handler(self, client_socket):
        while True:
            message = client_socket.recv(1024)
            print(message)

            for client in self.members:
                if client != client_socket:
                    client.send(message)
            time.sleep(1)


if __name__ == "__main__":
    server = Server('127.0.0.1', 6555)
