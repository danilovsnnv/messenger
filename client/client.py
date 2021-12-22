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
Window.clearcolor = (.85, .85, .85, 1)

SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCKET_CONNECTED = False
IP = '127.0.0.1'
PORT = 5555
USERNAME = ''
CHAT_USERNAME = ''
STORAGE = message_storage.MessageStorage()


class ScreenManagement(ScreenManager):
    pass


class StartScreen(Screen):
    """
    Начальный экран, отображаемый при входе
    """

    def check_socket(self, next_screen_name: str):
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
        accept = SOCKET.recv(1024).decode("utf-8")
        if accept == 'True':
            threading.Thread(target=self.manager.screens[-1].listen).start()
            self.manager.screens[-2].build_screen()
            self.manager.current = 'messages'
        else:
            self.error_label_widget.text = 'Неверный логин или пароль'


class RegistrationScreen(Screen):
    """
    Экран регистрации
    """

    def send_user_data(self):
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
                    pub_key_file.write(str(pubkey_pem))
                    priv_key_file = open("privkey.txt", "w")
                    priv_key_file.write(str(privkey_pem))
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
        accept = SOCKET.recv(1024).decode("utf-8")
        if accept == 'True':
            threading.Thread(target=self.manager.screens[-1].listen).start()
            self.manager.screens[-2].build_screen()
            self.manager.current = 'messages'
        else:
            self.error_label_widget.text = 'Данный пользователь уже существует'


class MessagesScreen(Screen):
    """
    Экран выбора переписки
    """
    in_search = False
    is_empty = False

    def build_screen(self, instance=''):
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
            button = Button(text=user, font_size=20, on_press=self.to_chat)
            self.layout_widget.add_widget(button)

    def to_chat(self, instance):
        chat_screen = self.manager.screens[-1]
        chat_screen.chat_widget.text = ''
        global CHAT_USERNAME
        CHAT_USERNAME = instance.text
        messages = STORAGE.get_messages(CHAT_USERNAME)
        for message in messages:
            chat_screen.chat_widget.text += ('[' + message[0] + '] ' + message[1] + '\n')
        self.manager.current = 'chat'

    def search_users(self):
        self.in_search = True
        if len(self.search_widget.text) < 3:
            self.rebuild([])
        else:
            SOCKET.send(('&search_users&' + self.search_widget.text).encode('utf-8'))

    def rebuild(self, users):
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
            if user[1:-1] == USERNAME:
                continue
            button = Button(text=user[1:-1], font_size=20, on_press=self.to_chat)
            self.layout_widget.add_widget(button)

    def add_chat(self, username: str):
        if self.in_search:
            return
        if self.is_empty:
            self.delete_buttons()
        button = Button(text=username, font_size=20, on_press=self.to_chat)
        self.layout_widget.add_widget(button)

    def delete_buttons(self):
        if self.layout_widget.children:
            self.layout_widget.clear_widgets()


class SearchScreen(Screen):
    pass


class ChatScreen(Screen):
    """
    Экран переписки
    """

    def send_message(self):
        current_text = self.chat_input_widget.text
        if form_check.check_empty_message(current_text):
            return
        self.chat_widget.text += '[' + USERNAME + '] ' + current_text + '\n'
        SOCKET.send(('&' + USERNAME + '&' + CHAT_USERNAME + '&' + current_text).encode('utf-8'))
        if STORAGE.contains_chat(CHAT_USERNAME):
            STORAGE.add_message(CHAT_USERNAME, USERNAME, current_text)
        else:
            STORAGE.add_message_in_new_chat(CHAT_USERNAME, USERNAME, current_text)
        self.chat_input_widget.text = ''

    def listen(self):
        while True:
            message = SOCKET.recv(1024).decode('utf-8').split('&', 2)[1::]
            if message == ['']:
                continue
            if message[0] == 'search_result':
                self.manager.screens[-2].rebuild(message[1][1:-1].replace(' ', '').split(','))
                continue
            if STORAGE.contains_chat(message[0]):
                STORAGE.add_message(message[0], message[0], message[1])
            else:
                STORAGE.add_message_in_new_chat(message[0], message[0], message[1])
                self.manager.screens[-2].add_chat(message[0])
            if message[0] == CHAT_USERNAME:
                self.chat_widget.text += '[' + message[0] + '] ' + message[1] + '\n'


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
