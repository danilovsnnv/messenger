import os
import datetime

from sqlalchemy import create_engine, Integer, String, Column, ForeignKey, DateTime, Boolean, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker

BDPATH = 'dbase.db'

base = declarative_base()
engine = create_engine('sqlite:///' + BDPATH + '?check_same_thread=False', echo=True)
session = sessionmaker(bind=engine)()


class Users(base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=True, unique=True)
    hash = Column(Integer, nullable=False, unique=False)
    open_key = Column(String, nullable=True)


class Messages(base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    user_from = Column(String(32), ForeignKey('users.username'))
    user_to = Column(String(32), ForeignKey('users.username'))
    time = Column(DateTime, nullable=False)
    message = Column(String, nullable=False)
    unreceived = Column(Boolean, nullable=False)


if not os.path.exists(BDPATH):
    base.metadata.create_all(engine)
    session.commit()


def add_user(username: str, data: str, key: str) -> bool:
    """
    Поиск пользователя в базе данных
         :param username: Имя пользователя
         :param data: Строка логин + пароль
         :param key: Открытый RSA ключ

         :return True: Пользователь существует в базе данных
         :return False: Пользователя нет или введены неверные данные
    """
    user_exists = has_user(username, data)
    if not user_exists:
        session.add(Users(username=username, hash=hash(data), open_key=key))
        session.commit()
    return not user_exists


def has_user(username: str, data: str) -> bool:
    """
    Поиск пользователя в базе данных
        :param username: Имя пользователя
        :param data: Строка логин + пароль

        :return: True: Пользователь существует в базе данных
        :return: False: Пользователя нет или введены неверные данные
    """
    return session.query(exists().where(Users.username == username and
                                        Users.hash == hash(data))).scalar()


def get_users_list(username_part: str) -> str:
    """
    Поиск пользователей по логину или его части
    :param username_part: Строка с логином
    :return: Строка с разделителями, содержащая имена пользователей или пустая строка,
    если пользователи не были найдены или запрос слишком короткий
    """
    users = session.query(Users.username).filter(Users.username.ilike(username_part + '%')).all()
    users_str = ''
    for user in users:
        users_str += '==&==' + str(user[0])
    return users_str


def add_message(user_from: str, user_to: str, message: str, unreceived: bool, time=None):
    """
    Добавление информации о сообщении в базу данных
        :param user_from: Имя пользователя-отправителя
        :param user_to: Имя пользователя-адресата
        :param message: Текст сообщения
        :param unreceived: Являяется ли сообщение непрочитанным
        :param time: Время отправки сообщения (по умолчанию текущее время)
    """
    if time is None:
        time = datetime.datetime.now()
    session.add(Messages(user_from=user_from, user_to=user_to, time=time, message=message, unreceived=unreceived))
    session.commit()


def get_messages(username: str):
    """
    Ищет неполучаенные сообщения для конкретного пользователя, удаляет их и возвращает
    :param username: Имя пользователя для поиска
    :return: Список сообщений
    """
    messages = session.query(Messages).filter(Messages.user_to == username).all()
    message_str = ''
    for message in messages:
        message_str += '==&==' + str(message.user_from) + '==&==' + str(message.message) + '==&==' \
                       + str(message.time) + '==&==' + str(message.unreceived)
        message.unreceived = False
    session.commit()
    return message_str


def get_open_key(username: str) -> str:
    """
    Получает открытый ключ по логину пользователя
    :param username: Имя пользователя
    :return: Открытый ключ пользователя
    """
    user = session.query(Users).filter(Users.username == username).one()
    return user.open_key
