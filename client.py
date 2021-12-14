import socket
import threading

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.core.window import Window
from kivy.config import Config

import form_check

import rsa


Config.set('kivy', 'keyboard_mode', 'systemanddock')

Window.size = (480, 853)
Window.title = 'Messenger'
Window.clearcolor = (.85, .85, .85, 1)

SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = '127.0.0.1'
PORT = 6555
USERNAME = ''


class ScreenManagement(ScreenManager):
    pass


class StartScreen(Screen):
    def check_socket(self, next_screen_name: str):
        global SOCKET
        try:
            SOCKET.connect((IP, PORT))
            self.parent.current = next_screen_name
        except WindowsError:
            self.parent.current = 'connection_error'


class ConnectionErrorScreen(Screen):
    pass


class LoginScreen(Screen):
    def send_user_data(self):
        if form_check.check_login(self.login_widget.text) and form_check.check_password(self.password_widget.text):
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
            self.parent.current = 'chat'
            threading.Thread(target=self.parent.screens[-1].listen).start()
        else:
            self.error_label_widget.text = 'Неверный логин или пароль'


class RegistrationScreen(Screen):
    def send_user_data(self):
        if form_check.check_login(self.login_widget.text):
            if form_check.check_password(self.password1_widget.text):
                if self.password1_widget.text == self.password2_widget.text:
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
            self.parent.current = 'chat'
        else:
            self.error_label_widget.text = 'Данный пользователь уже существует'


class MessagesScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)


class ChatScreen(Screen):
    def send_message(self):
        current_text = self.chat_input_widget.text
        if current_text == '':
            return
        self.chat_widget.text += '[Вы] ' + current_text + '\n'
        self.chat_input_widget.text = ''
        SOCKET.send(('[Собеседник] ' + current_text).encode('utf-8'))

    def listen(self):
        while True:
            msg = SOCKET.recv(1024)
            self.chat_widget.text += msg.decode('utf-8') + '\n'


class ClientApp(App):

    def __init__(self):
        super().__init__()
        self.build_kv = Builder.load_file('client.kv')

    def build(self):
        return self.build_kv


if __name__ == '__main__':
    client = ClientApp()
    client.run()
