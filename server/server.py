import time
import socket
import threading

import database

import rsa


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
        """
        Подлючнеие новых пользователей
        """
        while True:
            client, address = self.server.accept()
            print(f'Connected: {client}')
            self.check_user_data(client)
            time.sleep(1)

    def check_user_data(self, client_socket: socket.socket):
        """
        Проверка данных пользователей при входе и регистрации
        :param client_socket: Сокет отправителя
        """
        pub_key_client_pem = client_socket.recv(1024)
        (pubkey, privkey) = rsa.newkeys(1024)
        client_socket.send(pubkey.save_pkcs1())

        username_secret = client_socket.recv(1024)
        data_secret = client_socket.recv(1024)
        username = rsa.decrypt(username_secret, privkey).decode('utf-8')
        data = rsa.decrypt(data_secret, privkey).decode('utf-8')
        if data[0] == 'l':
            accept = database.has_user(username, data[1:])
        elif data[0] == 'r':
            accept = database.add_user(username, data[1:], pub_key_client_pem)
        else:
            accept = False
        client_socket.send(str(accept).encode('utf-8'))
        if accept:
            threading.Thread(target=self.message_handler, args=(client_socket,)).start()
            self.members_dict[username] = client_socket
            # Отправка сообщений для синхронизации
            self.send_messages(client_socket, username)
        else:
            self.check_user_data(client_socket)

    def message_handler(self, client_socket: socket.socket):
        """
        Приём сообщений, обработка команд, отправка сообщений адресату
        :param client_socket: Сокет отправителя
        """
        while True:
            # Получение сообщения
            message = client_socket.recv(1024).decode("utf-8").split('&', 3)[1::]
            if message[0] == 'search_users':
                # Если это запрос поиска пользователей
                self.search_users(client_socket, message[1])
                continue
            try:
                # Если пришло обычное сообщение
                receiver_socket = self.members_dict[message[1]]
                # Проверка на онлайн
                online = self.online_check(receiver_socket)
                if online:
                    receiver_socket.send(('&' + message[0] + '&' + message[2]).encode('utf-8'))
                    # Добавление сообщения в базу данных
                    database.add_message(message[0], message[1], message[2], unreceived=False)
                database.add_message(message[0], message[1], message[2], unreceived=True)
            except KeyError:
                database.add_message(message[0], message[1], message[2], unreceived=True)
            time.sleep(1)

    @staticmethod
    def send_messages(client_socket: socket.socket, username: str):
        """
        Поиск и отправка сообщений для синхронизации
        :param client_socket: Сокет клиента для синхронизации
        :param username: Имя пользователя для поиска сообщений
        """
        messages = database.get_messages(username)
        client_socket.send(('&synchronize_messages&' + str(messages)).encode('utf-8'))

    @staticmethod
    def search_users(client_socket: socket.socket, username: str):
        """
        Ищет пользователей по строке
        :param client_socket: Сокет клиента для отправки списка
        :param username: Имя пользователя для поиска
        """
        users = database.get_users_list(username)
        client_socket.send(('&search_result&' + users).encode('utf-8'))

    @staticmethod
    def online_check(client_socket: socket.socket) -> bool:
        """
        Проверка сокета на онлайн
        :param client_socket: Сокет для проверки
        :return: Онлайн пользователь или нет
        """
        try:
            client_socket.send('&'.encode('utf-8'))
            return True
        except WindowsError:
            return False


if __name__ == "__main__":
    server = Server('127.0.0.1', 6666)
