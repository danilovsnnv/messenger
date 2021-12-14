import time
import socket
import threading

import database


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.members_dict = {}

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen(0)
        threading.Thread(target=self.connect).start()

        print(f'Listening at {self.ip}:{self.port}')

    def connect(self):
        """Подлючнеие новых пользователей"""
        while True:
            client, address = self.server.accept()
            print(f'Connected: {client}')
            threading.Thread(target=self.check_user_data, args=(client,)).start()
            time.sleep(1)

    def check_user_data(self, client_socket: socket.socket):
        """Проверка данных пользователей при входе и регистрации"""
        username = str(client_socket.recv(1024))[2:-1]
        data = str(client_socket.recv(1024))[2:-1]
        if data[0] == 'l':
            accept = database.has_user(username, data[1:])
        elif data[0] == 'r':
            accept = database.add_user(username, data[1:], "open_key_here")
        else:
            accept = False
        client_socket.send(str(accept).encode('utf-8'))
        if accept:
            threading.Thread(target=self.message_handler, args=(client_socket,)).start()
            self.members_dict[username] = client_socket
        else:
            threading.Thread(target=self.check_user_data, args=(client_socket,)).start()

    def message_handler(self, client_socket: socket.socket):
        """Приём сообщений и их отправка в общий чат"""
        while True:
            message = str(client_socket.recv(1024))[2:-1].split('&', 3)[1::]
            receiver_socket = self.members_dict[message[0]]
            online = self.online_check(receiver_socket)
            if online:
                receiver_socket.send(('&' + message[1] + '&' + message[2]).encode('utf-8'))
                database.add_message(message[0], message[1], message[2])
            else:
                database.add_unreceived_message(message[0], message[1], message[2])

            for client in self.members_dict.values():
                if client != client_socket:
                    client.send(message)
            time.sleep(1)

    @staticmethod
    def online_check(client_socket: socket.socket) -> bool:
        """Проверка сокета на онлайн"""
        try:
            client_socket.send('&'.encode('utf-8'))
            return True
        except WindowsError:
            return False


if __name__ == "__main__":
    server = Server('127.0.0.1', 6555)
