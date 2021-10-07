import socket
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class Client(App):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    main_layout = BoxLayout(orientation='vertical')
    btn_layout = BoxLayout(orientation='horizontal')
    chat = TextInput(multiline=True, readonly=True, font_size=30)
    msg_input = TextInput(multiline=True, font_size=30)
    send_button = Button(text='Отправить', pos_hint={"center_x": 0.5, "center_y": 0.5})
    clear_button = Button(text='Очистить', pos_hint={"center_x": 0.5, "center_y": 0.5})
    connect_button = Button(text='Подключиться', pos_hint={"center_x": 0.5, "center_y": 0.5})

    def build(self):
        self.main_layout.add_widget(self.chat)
        self.main_layout.add_widget(self.msg_input)
        self.send_button.bind(on_press=self.send_message)
        self.btn_layout.add_widget(self.send_button)
        self.clear_button.bind(on_press=self.clear)
        self.btn_layout.add_widget(self.clear_button)
        self.main_layout.add_widget(self.btn_layout)
        self.connect_button.bind(on_press=self.connect_socket)
        self.main_layout.add_widget(self.connect_button)

        return self.main_layout

    def connect_socket(self, instnce):
        self.s.connect(('127.0.0.1', 6555))
        threading.Thread(target=self.listen, args=(self.s,), daemon=True).start()

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
    app = Client()
    app.run()
