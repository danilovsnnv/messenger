import re


def check_login(log: str, pattern=r'[a-zA-Z][a-zA-Z0-9]{,31}$'):
    """
    Паттерн по умолчанию проверяет, что логин написан на английском, начинается с буквы, содержит не более 32 символов
    и не содержит спецсимволов
    :param log: Логин пользователя для проверки
    :param pattern: Паттерн для проверки правильности ввода

    :return True: Логин подходит
    :return False: Логин не подходит
    """
    return re.match(pattern, log)


def check_password(pwd: str, pattern=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'):
    """
    Паттерн по умолчанию задает пароль из не менее восьми символов, содержащий английские буквы в
    разных регистрах и цифры
    :param pwd: Пароль пользователя для проверки:
    :param pattern: Паттерн для проверки правильности ввода

    :return True: Логин подходит
    :return False: Логин не подходит
    """

    return re.match(pattern, pwd)


def check_empty_message(msg: str):
    """
    Функция проверяет, состоит ли сообщение из пробелов или переноса
    :param msg: Сообщение для проверки
    :return: True или False, в зависимости от того, пустое сообщение или нет
    """
    return msg == '' or msg.isspace() or msg == '\n' or '==!==' in msg or '==&==' is msg or '==%==' in msg
