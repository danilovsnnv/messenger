import socket
import threading


def listen(s: socket.socket):
    while True:
        msg = s.recv(1024)
        print('\r\r' + msg.decode('utf-8') + '\n', end='')


def connect(host: str = '127.0.0.1', port: int = 6555):
    user_name = input('Введите никнейм: ')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((host, port))

    threading.Thread(target=listen, args=(s,), daemon=True).start()

    s.send((user_name + ' подключатеся к чату').encode('utf-8'))

    while True:
        msg = input('[Вы]: ')
        s.send(('[' + user_name + '] ' + msg).encode('utf-8'))


if __name__ == '__main__':
    connect()
