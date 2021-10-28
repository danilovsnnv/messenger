import socket
import threading

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.core.window import Window
from kivy.config import Config

Config.set('kivy', 'keyboard_mode', 'systemanddock')

Window.size = (480, 853)
Window.title = 'Messenger'
Window.clearcolor = (.85, .85, .85, 1)


class ClientApp(App):
    class ScreenManagement(ScreenManager):
        pass

    class StartScreen(Screen):
        pass

    class RegistrationScreen(Screen):
        pass

    class LoginScreen(Screen):
        pass

    class ChatScreen(Screen):
        def connect_socket(self):
            try:
                self.s.connect((self.ip, self.port))
                threading.Thread(target=self.listen, args=(self.s,), daemon=True).start()
            except Exception:
                self.chat_widget.text += 'Не удалось подключиться к серверу \n'

        def send_message(self):
            current_text = self.chat_input_widget.text
            if current_text == '':
                return
            self.chat_widget.text += '[Вы] ' + current_text + '\n'
            self.s.send(('[Собеседник] ' + current_text).encode('utf-8'))
            self.chat_input_widget.text = ''

        def listen(self, instance):
            while True:
                msg = self.s.recv(1024)
                self.chat_widget.text += msg.decode('utf-8') + '\n'

    def __init__(self, ip: str, port: int):
        super().__init__()
        self.ip = ip
        self.port = port
        self.build_kv = Builder.load_file('client.kv')

    def build(self):
        return self.build_kv


if __name__ == '__main__':
    client = ClientApp('127.0.0.1', 6555)
    client.run()
