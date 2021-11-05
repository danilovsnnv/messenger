import time
import socket
import threading

import database


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.members = []
        self.adresa = []

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
                self.adresa.append(address)
                print(client)
                threading.Thread(target=self.check_user_data, args=(client,)).start()
                # client.send('Успешное подключение к чату!'.encode('utf-8'))
            time.sleep(1)

    def check_user_data(self, client_socket):
        data = client_socket.recv(1024)
        if data[0]== 'l':
            accept = database.check_user(data[1::])
            client_socket.send(accept.encode('utf-8'))
            if accept:
                threading.Thread(target=self.message_handler, args=(client_socket,)).start()
            else:
                threading.Thread(target=self.connect, args=(client_socket,)).start()
        if data[0] == 'r':
            database.add_user(data[1::])
            threading.Thread(target=self.message_handler, args=(client_socket,)).start()

    def message_handler(self, client_socket):
        while True:
            message = client_socket.recv(1024)

            for client in self.members:
                if client != client_socket:
                    client.send(message)
            time.sleep(1)


if __name__ == "__main__":
    server = Server('127.0.0.1', 6555)
