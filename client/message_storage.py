import json
import datetime


class MessageStorage:
    """
    Локальное хранилище сообщений для клиента
    """

    def __init__(self):
        """
        Создание или чтение JSON файла, создание словаря
        """
        with open("messages.json", "w") as self.json_file:
            self.messages_dict = {}
            json.dump({}, self.json_file, indent=4)

    def save(self):
        with open("messages.json", "w") as self.json_file:
            json.dump(self.messages_dict, self.json_file, indent=4)

    def add_message(self, chat: str, user: str, text: str, unread: bool, time=None):
        """
        Добавление сообщения в JSON файл
        :param chat: Название чата
        :param user: Имя пользователя, отправившего сообщение
        :param text: Текст сообщения
        :param unread: Прочитано ли сообщение
        :param time: Время отправки сообщения
        """
        if time is None:
            time = datetime.datetime.now()
        try:
            self.messages_dict[chat].append([user, text, str(time), unread])
        except KeyError:
            self.messages_dict[chat] = [[user, text, str(time), True]]
        self.save()

    def get_messages(self, username: str) -> dict:
        """
        Находит в хранилище переписку с конкретным пользователем и возвращает сообщения оттуда
        :param username: Имя пользователя, чат с которым нужно получить
        :return: Список с сообщениями из чата
        """
        try:
            for i in range(len(self.messages_dict[username])):
                if self.messages_dict[username][i][-1]:
                    self.messages_dict[username][i][-1] = False
            self.save()
            return self.messages_dict[username]
        except KeyError:
            return []

    def get_users_list(self):
        """
        Возвращает список пользователей, с которыми есть переписка
        :return: Список пользователей, с которыми начат чат
        """
        return list(dict(sorted(self.messages_dict.items(), key=lambda x: x[1][-1][-2], reverse=True)))

    def contains_chat(self, username):
        """
        Проверяет начат ли чат с пользователем
        :param username: Имя пользователя
        :return: True или False в зависимости от того, найден ли чат
        """
        return username in list(self.messages_dict)

    def has_unread(self, username):
        """
        Проверяет наличие непрочитанных сообщений в чате с пользователем
        :param username: Имя пользователя
        :return: Есть ли непрочитанные сообщения
        """
        return True in sum(self.messages_dict[username], [])

    def update_storage(self, messages: list):
        """
        Обновляет хранилище сообщениями, полученными с сервера
        :param messages: Список с сообщениями
        """
        if messages == ['']:
            return
        self.messages_dict.clear()
        while messages:
            self.add_message(messages[0], messages[0], messages[1], messages[2], messages[3])
            del messages[0:4]
