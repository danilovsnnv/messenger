import socket
import threading

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.core.window import Window
from kivy.config import Config

import form_check
import message_storage

import rsa

Config.set('kivy', 'keyboard_mode', 'systemanddock')

Window.size = (480, 853)
Window.title = 'Messenger'
Window.clearcolor = (.9, .9, .9, 1)

SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Сокет пользователя
SOCKET_CONNECTED = False  # Статус подключения сокета
IP = '127.0.0.1'  # Ip клиента
PORT = 6666  # Порт клиента
USERNAME = ''  # Имя пользователя
CHAT_USERNAME = ''  # Имя пользователя, с которым ведётся переписка
STORAGE = message_storage.MessageStorage()  # Объект локального хранилища сообщений


class ScreenManagement(ScreenManager):
    """
    Менеджер экранов
    """
    pass


class StartScreen(Screen):
    """
    Начальный экран, отображаемый при входе
    """

    def check_socket(self, next_screen_name: str):
        """
        Проверка подключения к серверу
        :param next_screen_name: Имя экрана для перехода
        """
        global SOCKET, SOCKET_CONNECTED
        if not SOCKET_CONNECTED:
            try:
                SOCKET.connect((IP, PORT))
                SOCKET_CONNECTED = True
                self.parent.current = next_screen_name
            except WindowsError:
                self.parent.current = 'connection_error'
        else:
            self.parent.current = next_screen_name


class ConnectionErrorScreen(Screen):
    """
    Экран, выводящий ошибку при подключении к серверу
    """
    pass


class LoginScreen(Screen):
    """
    Экран входа в аккаунт
    """

    def send_user_data(self):
        """
        Отправка данных пользователя для входа
        """
        if form_check.check_login(self.login_widget.text) and form_check.check_password(self.password_widget.text):
            global USERNAME
            USERNAME = self.login_widget.text
            pub_key_file = open("pubkey.txt", "r")
            pubkey_pem = pub_key_file.read().encode("utf-8")
            pub_key_file.close()
            SOCKET.send(pubkey_pem)
            server_pub_key = rsa.PublicKey.load_pkcs1(SOCKET.recv(1024), 'PEM')
            data = 'l' + str(self.login_widget.text) + str(self.password_widget.text)
            secret_data = rsa.encrypt(data.encode('utf-8'), server_pub_key)
            secret_login = rsa.encrypt(self.login_widget.text.encode('utf-8'), server_pub_key)
            SOCKET.send(secret_login)
            SOCKET.send(secret_data)
            threading.Thread(target=self.accept_handler).start()
        else:
            self.error_label_widget.text = 'Проверьте введённые данные'

    def accept_handler(self):
        """
        Приём подтверждения для входа
        """
        accept = SOCKET.recv(1024).decode("utf-8")
        if accept == 'True':
            threading.Thread(target=self.manager.screens[-1].listen).start()
        else:
            self.error_label_widget.text = 'Неверный логин или пароль'


class RegistrationScreen(Screen):
    """
    Экран регистрации
    """

    def send_user_data(self):
        """
        Отправка данных пользователя при регистрации
        """
        if form_check.check_login(self.login_widget.text):
            if form_check.check_password(self.password1_widget.text):
                if self.password1_widget.text == self.password2_widget.text:
                    global USERNAME
                    USERNAME = self.login_widget.text
                    # Создание ключей и запись их в файл
                    (pubkey, privkey) = rsa.newkeys(1024)
                    pubkey_pem = pubkey.save_pkcs1()  # (format='PEM')
                    privkey_pem = privkey.save_pkcs1()
                    pub_key_file = open("pubkey.txt", "w")
                    pub_key_file.write(pubkey_pem.decode('utf-8'))
                    priv_key_file = open("privkey.txt", "w")
                    priv_key_file.write(privkey_pem.decode('utf-8'))
                    pub_key_file.close()
                    priv_key_file.close()
                    # Конец создания ключей

                    SOCKET.send(pubkey_pem)
                    server_pub_key_pem = SOCKET.recv(1024)
                    server_pub_key = rsa.PublicKey.load_pkcs1(server_pub_key_pem, 'PEM')
                    data = 'r' + str(self.login_widget.text) + str(self.password1_widget.text)
                    secret_data = rsa.encrypt(data.encode('utf-8'), server_pub_key)
                    secret_login = rsa.encrypt(self.login_widget.text.encode('utf-8'), server_pub_key)
                    SOCKET.send(secret_login)
                    SOCKET.send(secret_data)
                    threading.Thread(target=self.accept_handler).start()
                else:
                    self.error_label_widget.text = 'Введённые пароли не совпадают'
            else:
                self.error_label_widget.text = 'Пароль должен содержать не менее восьми символов, ' \
                                               'английские буквы в разных регистрах и цифры'
        else:
            self.error_label_widget.text = 'Логин должен быть написан на английском, начинаться с буквы, ' \
                                           'содержать не более 32 символов и не содержать спецсимволов'

    def accept_handler(self):
        """
        Приём подтверждения для регистрации
        """
        accept = SOCKET.recv(1024).decode("utf-8")
        if accept == 'True':
            threading.Thread(target=self.manager.screens[-1].listen).start()
        else:
            self.error_label_widget.text = 'Данный пользователь уже существует'


class MessagesScreen(Screen):
    """
    Экран выбора переписки
    """
    in_search = False  # Производится ли поиск
    is_empty = False  # Есть ли чаты

    def build_screen(self, instance=''):
        """
        Создание экрана переписок, добавление кнопок с чатами
        """
        self.in_search = False
        self.delete_buttons()
        users = STORAGE.get_users_list()
        if not users:
            label = Label(text='Сообщений пока нет. Найдите собеседника через поиск и начните первый чат!',
                          text_size=self.size, halign='center', color=[0, 0, 0, 1],
                          pos_hint={'center_x': .5, 'top': 1})
            self.layout_widget.add_widget(label)
            self.is_empty = True
            return

        for user in users:
            button = Button(text=user, font_size=20, on_press=self.to_chat,
                            background_color=self.get_button_color(user))
            self.layout_widget.add_widget(button)

    def to_chat(self, instance):
        chat_screen = self.manager.screens[-1]
        chat_screen.chat_widget.text = ''
        global CHAT_USERNAME
        CHAT_USERNAME = instance.text
        chat_screen.action_text_widget.title = CHAT_USERNAME
        messages = STORAGE.get_messages(CHAT_USERNAME)
        for message in messages:
            chat_screen.chat_widget.text += ('[' + message[0] + '] ' + message[1] + '\n')
        self.manager.current = 'chat'

    @staticmethod
    def get_button_color(username: str) -> list:
        """
        Возвращает цвет для кнопки, в зависимости от того, есть ли новые сообщения в чате
        :param username: Имя пользователя для проверки
        :return: Список с цветом кнопки
        """
        if STORAGE.has_unread(username):
            return [0, 0, 1, 1]
        return [1, 1, 1, 1]

    def search_users(self):
        """
        Осуществление поиска по пользователям
        """
        self.in_search = True
        if len(self.search_widget.text) < 3:
            self.rebuild([])
        else:
            SOCKET.send(('&search_users&' + self.search_widget.text).encode('utf-8'))

    def rebuild(self, users):
        """
        Переработка экрана переписок под результаты поиска
        :param users: Список найденных пользователей
        """
        self.delete_buttons()
        exit_button = Button(text='Вернуться к перепискам', font_size=20, background_color=[0, 0, 1, 1],
                             on_press=self.build_screen)
        self.layout_widget.add_widget(exit_button)

        if not users:
            label = Label(text='Не найдено пользователей или запрос содержит меньше 3х символов',
                          text_size=self.size, halign='center', color=[0, 0, 0, 1],
                          pos_hint={'center_x': .5, 'top': 1})
            self.layout_widget.add_widget(label)
            return

        for user in users:
            if user == USERNAME:
                continue
            button = Button(text=user, font_size=20, on_press=self.to_chat)
            self.layout_widget.add_widget(button)

    def update_chats(self):
        """
        Обновить список чатов
        """
        if self.in_search:
            return
        self.build_screen()

    def delete_buttons(self):
        """
        Удалить кнопки с экрана чатов
        """
        if self.layout_widget.children:
            self.layout_widget.clear_widgets()


class SearchScreen(Screen):
    pass


class ChatScreen(Screen):
    """
    Экран переписки
    """
    def send_message(self):
        """
        Отправка запроса ключа
        """
        SOCKET.send(("&get_keys&" + CHAT_USERNAME).encode('utf-8'))

    def listen(self):
        """
        Получение сообщений, запускается из потока
        """
        priv_key_file = open("privkey.txt", "r")
        privkey_pem = priv_key_file.read()
        privkey = rsa.PrivateKey.load_pkcs1(privkey_pem, "PEM")
        while True:
            # Получение сообщения
            message = SOCKET.recv(2048)
            try:
                # Попытка расшифровать как сообщение
                [message, secret_data1] = message.split(sep="==%==".encode('utf-8'))
            except ValueError:
                pass
            try:
                # Попытка рассшифровать как список сообщений для синхронизации
                [message, all_messages] = message.split(sep="==!==".encode('utf-8'))
            except ValueError:
                pass
            # Перевод в стркоу и парсинг
            message = message.decode('utf-8').split('&', 2)[1::]
            if message == ['']:
                continue
            if message[0] == 'key':
                # Если пришёл ключ
                chat_pybkey_pem = message[1]
                chat_pubkey = rsa.PublicKey.load_pkcs1(chat_pybkey_pem, "PEM")
                current_text = self.chat_input_widget.text
                # Проверка на то, пустое ли сообщение
                if form_check.check_empty_message(current_text):
                    return
                self.chat_widget.text += '[' + USERNAME + '] ' + current_text + '\n'
                secret_data = rsa.encrypt(current_text.encode('utf-8'), chat_pubkey)
                SOCKET.send(('&' + USERNAME + '&' + CHAT_USERNAME + '==%==').encode('utf-8')+secret_data)
                STORAGE.add_message(CHAT_USERNAME, USERNAME, current_text, 'False')
                self.chat_input_widget.text = ''
            else:
                # Если пришёл список пользователей для поиска
                if message[0] == 'search_result':
                    self.manager.screens[-2].rebuild(message[1].split('==&==')[1::])
                    continue
                # Если пришли непрочитанные сообщения после входа
                if message[0] == 'unreceived_messages':
                    all_messages_array = all_messages.split(sep='==@=='.encode('utf-8'))[1::]
                    for i in range(len(all_messages_array)):
                        if i % 3 == 0 or i % 3 == 2:
                            all_messages_array[i] = all_messages_array[i].decode('utf-8')
                        if i % 3 == 1:
                            all_messages_array[i] = rsa.decrypt(all_messages_array[i], privkey).decode('utf-8')
                    STORAGE.update_storage(all_messages_array)
                    self.manager.screens[-2].build_screen()
                    self.manager.current = 'messages'
                    continue
                # Если принято обычное сообщение. Происходит обновление хранилища и обновление списка чатов
                decrypted_message = rsa.decrypt(secret_data1, privkey).decode('utf-8')
                if message[0] == CHAT_USERNAME:
                    # Если сообщение от текущего собеседника
                    self.chat_widget.text += '[' + message[0] + '] ' + decrypted_message + '\n'
                    STORAGE.add_message(message[0], message[0], decrypted_message, 'False')
                else:
                    # Если соощение от другого собеседника
                    STORAGE.add_message(message[0], message[0], decrypted_message, 'True')
                self.manager.screens[-2].update_chats()

    def back(self):
        """
        Возвращение к экрану чатов
        """
        global CHAT_USERNAME
        CHAT_USERNAME = ''
        self.chat_input_widget.text = ''
        self.manager.screens[-2].build_screen()
        self.manager.current = 'messages'


class ClientApp(App):
    """
    Класс клиента
    """
    def __init__(self):
        super().__init__()
        self.build_kv = Builder.load_file('client.kv')

    def build(self):
        return self.build_kv


if __name__ == '__main__':
    client = ClientApp()
    client.run()
