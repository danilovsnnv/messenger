import socket
import threading

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

from kivy.core.window import Window

Window.size = (480, 800)
Window.title = 'Messenger'


class Client(App):

    def __init__(self, ip: str, port: int):
        super().__init__()

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.main_layout = BoxLayout(orientation='vertical')
        self.scroll = ScrollView(size=(Window.width, Window.height), bar_width=12)
        self.chat_layout = BoxLayout(orientation='vertical')
        self.control_layout = BoxLayout(orientation='vertical')
        self.btn_layout = BoxLayout(orientation='horizontal')
        self.chat = TextInput(multiline=True, readonly=True, font_size=30)
        self.input_layout = BoxLayout(orientation='horizontal')
        self.msg_input = TextInput(multiline=True, font_size=30)
        self.send_button = Button(text='Отпр.',
                                  pos_hint={"center_x": 0.5, "center_y": 0.5}, size=(10, 10))
        self.connect_button = Button(text='Подключиться',
                                     pos_hint={"center_x": 0.5, "center_y": 0.5})

    def build(self):
        self.chat_layout.add_widget(self.chat)
        self.scroll.add_widget(self.chat_layout)
        self.main_layout.add_widget(self.scroll)
        self.input_layout.add_widget(self.msg_input)

        self.send_button.bind(on_press=self.send_message)
        self.input_layout.add_widget(self.send_button)
        self.control_layout.add_widget(self.input_layout)

        self.connect_button.bind(on_press=self.connect_socket)
        self.control_layout.add_widget(self.connect_button)

        self.main_layout.add_widget(self.control_layout)

        return self.main_layout

    def connect_socket(self, instance):
        try:
            self.s.connect((self.ip, self.port))
            threading.Thread(target=self.listen, args=(self.s,), daemon=True).start()
        except Exception:
            self.chat.text += 'Не удалось подключиться к серверу \n'

    def send_message(self, instance):
        current_text = self.msg_input.text
        if self.msg_input.text == '':
            return
        self.chat.text += '[Вы] ' + current_text + '\n'
        self.s.send(('[Собеседник] ' + current_text).encode('utf-8'))
        self.msg_input.text = ''

    def clear(self, instance):
        self.msg_input.text = ''

    def listen(self, instance):
        while True:
            msg = self.s.recv(1024)
            self.chat.text += msg.decode('utf-8') + '\n'


if __name__ == '__main__':
    client = Client('127.0.0.1', 6555)
    client.run()
