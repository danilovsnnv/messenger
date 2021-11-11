import re
def check_login(log, pattern = r'[a-zA-Z][a-zA-Z0-9]{,31}$'):
  # Паттерн по умолчанию проверяет, что логин написан на английском, начинается с буквы, содержит не более 32 символов и не содержит спецсимволов
  if re.match(pattern, log):
    return True
  else:
    return False

def check_passpord(pwd, pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'):
  # Паттерг по умолчанию задает пароль из не менее восьми символов, содержащий английские буквы в разных регистрах и цифры
  if re.match(pattern, pwd):
    return True
  else:
    return False

