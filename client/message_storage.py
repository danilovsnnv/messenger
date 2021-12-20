import json
import os
import datetime


class MessageStorage:
    def __init__(self):
        if not os.path.exists('messages.json'):
            self.json_file = open("messages.json", "w")
            self.messages_dict = {}
        else:
            with open('messages.json', 'r') as self.json_file:
                self.messages_dict = json.load(self.json_file)

    def add_message(self, chat: str, user: str, text: str):
        """
        Добавление сообщения в JSON файл
        :param chat: Название чата
        :param user: Имя пользователя, отправившего сообщение
        :param text: Текст сообщения
        """
        try:
            self.messages_dict[chat].append([user, text, str(datetime.datetime.now())])
            if len(self.messages_dict[chat]) > 100:
                del self.messages_dict[chat][0]
        except KeyError:
            self.messages_dict[chat] = [[user, text, str(datetime.datetime.now())]]
        finally:
            with open("messages.json", "w") as json_file:
                json.dump(self.messages_dict, json_file, indent=4)

    def get_messages(self, username: str) -> dict:
        """
        Находит в хранилище переписку с конкретным пользователем и возвращает сообщения оттуда
        :param username: Имя пользователя, чат с которым нужно получить
        :return: Список с сообщениями из чата
        """
        try:
            return self.messages_dict[username]
        except KeyError:
            return []

    def get_users_list(self):
        return list(self.messages_dict)


if __name__ == '__main__':
    m = MessageStorage()
    m.get_users_list()

