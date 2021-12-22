import json
import os
import datetime


class MessageStorage:
    """
    Локальное хранилище сообщений для клиента
    """

    def __init__(self):
        """
        Создание или чтение JSON файла, создание словаря
        """
        if not os.path.exists('messages.json'):
            with open("messages.json", "w") as self.json_file:
                self.messages_dict = {}
                json.dump(self.messages_dict, self.json_file, indent=4)
        else:
            with open('messages.json', 'r') as self.json_file:
                self.messages_dict = json.load(self.json_file)

    def add_message(self, chat: str, user: str, text: str, time=datetime.datetime.now()):
        """
        Добавление сообщения в JSON файл
        :param chat: Название чата
        :param user: Имя пользователя, отправившего сообщение
        :param text: Текст сообщения
        :param time: Время отправки сообщения
        """
        self.messages_dict[chat].append([user, text, str(time)])
        if len(self.messages_dict[chat]) > 100:
            del self.messages_dict[chat][0]
        with open("messages.json", "w") as json_file:
            json.dump(self.messages_dict, json_file, indent=4)

    def add_message_in_new_chat(self, new_chat: str, user: str, text: str, time=datetime.datetime.now()):
        """
        Создание нового чата и добавление сообщения в JSON файл
        :param new_chat: Название нового чата
        :param user: Имя пользователя, отправившего сообщение
        :param text: Текст сообщения
        :param time: Время отправки
        """
        self.messages_dict[new_chat] = [[user, text, str(time)]]
        with open("messages.json", "w") as self.json_file:
            json.dump(self.messages_dict, self.json_file, indent=4)

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
        """
        Возвращает список пользователей, с которыми есть переписка
        :return: Список пользователей, с которыми начат чат
        """
        return list(self.messages_dict)

    def contains_chat(self, username):
        """
        Проверяет начат ли чат с пользователем
        :param username: Имя пользователя
        :return: True или False в зависимости от того, найден ли чат
        """
        return username in list(self.messages_dict)

    def update_storage(self, messages_list: str):
        """
        Добавляет в хранилище новые неполученные сообщения
        :param messages_list: Строка с сообщениями
        """
        if messages_list == ['']:
            return
        while messages_list:
            if self.contains_chat(messages_list[0]):
                self.add_message(messages_list[0], messages_list[0], messages_list[1],
                                 messages_list[2])
            else:
                self.add_message_in_new_chat(messages_list[0], messages_list[0], messages_list[1],
                                             messages_list[2])

            del messages_list[0:3]
