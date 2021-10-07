from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class MainApp(App):

    main_layout = BoxLayout(orientation='vertical')
    btn_layout = BoxLayout(orientation='horizontal')
    chat = TextInput(multiline=False, readonly=True, font_size=55)
    msg_input = TextInput(multiline=True, font_size=55)
    send_button = Button(text='Отправить', pos_hint={"center_x": 0.5, "center_y": 0.5})
    clear_button = Button(text='Очистить', pos_hint={"center_x": 0.5, "center_y": 0.5})

    def build(self):
        self.main_layout.add_widget(self.chat)
        self.main_layout.add_widget(self.msg_input)
        self.send_button.bind(on_press=self.on_button_press)
        self.btn_layout.add_widget(self.send_button)
        self.clear_button.bind(on_press=self.on_button_press)
        self.btn_layout.add_widget(self.clear_button)
        self.main_layout.add_widget(self.btn_layout)

        return self.main_layout

    def on_button_press(self, instance):
        current_text = self.msg_input.text
        button_text = instance.text

        if button_text == 'Отправить':
            if self.msg_input.text == '':
                return
            self.chat.text += '[You] ' + current_text + '\n'
            self.msg_input.text = ''

        if button_text == 'Очистить':
            self.msg_input.text = ''


if __name__ == '__main__':
    app = MainApp()
    app.run()
