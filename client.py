import socket
import threading

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout

from kivy.core.window import Window

Window.size = (500, 1000)
Window.title = 'Messenger'


class ChatScreen(FloatLayout):
    def __init__(self, ip: str, port: int):
        super().__init__()

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port

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


class ClientApp(App):

    def __init__(self, ip: str, port: int):
        super().__init__()
        self.ip = ip
        self.port = port

    def build(self):
        return ChatScreen(self.ip, self.port)


if __name__ == '__main__':
    client = ClientApp('127.0.0.1', 6555)
    client.run()
