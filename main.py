# Спросить про асинхронность

import sqlite3
import re

# подключаемся к БД

connection = sqlite3.connect("application.db")
cursor = connection.cursor()

# Таблица USERS:
# userID INTEGER not null primary key autoincrement,
# login TEXT not null,
# password TEXT not null,
# email TEXT not null,
# name TEXT not null

PASSWORD_MIN_LENGTH = 8


def checking_email_correctness(email):
    # a.a@b1.c // a.a - address, b1 - domain, c - top_domain
    # address - латиница, числа, точки
    # domain - латиница, числа
    # top-domain - латиница в нижнем регистре

    address_domain = email.split('@')
    if len(address_domain) != 2:
        return False

    domain_top_domain = address_domain[1].split('.')
    if len(domain_top_domain) != 2:
        return False

    address = address_domain[0]
    domain = domain_top_domain[0]
    top_domain = domain_top_domain[1]

    # проверяем, что формат adress, domain и top_domain соблюден

    if not re.fullmatch(r'[a-zA-Z0-9.]+', address):
        return False
    if not re.fullmatch(r'[a-zA-Z0-9.]+', domain):
        return False
    if not re.fullmatch(r'[a-z]+', top_domain):
        return False

    return True


def checking_password_complexity(password, isnew=False):
    # что делает каждый if видно из возвращаемого значения
    if len(password) < PASSWORD_MIN_LENGTH:
        return f"Ваш {isnew * 'новый'} пароль слишком короткий. Минимальная длина пароля - {PASSWORD_MIN_LENGTH} символов"
    if password.upper() == password:
        return f"Ваш {isnew * 'новый'} пароль должен содержать хотя бы один строчный символ"
    if password.lower() == password:
        return f"Ваш {isnew * 'новый'} пароль должен содержать хотя бы один заглавный символ"
    if re.fullmatch(r'[a-zA-Z]+', password):
        return f"Ваш {isnew * 'новый'} пароль должен содержать хотя бы одну цифру"
    return None


def registration(login, password, name, email):
    # проверяем, что нет ни одной пустой строки
    if not all([len(login), len(password), len(name), len(email)]):
        return "Недопустимый формат регистрационной строки"

    # проверяем, что почта соответствует формату "a@b.c"
    if not checking_email_correctness(email):
        return "Некорректный email"

    # проверяем, что пользователя с таким логином не существует
    query = "SELECT * FROM USERS WHERE login=?"
    result = cursor.execute(query, (login,)).fetchall()
    if len(result):
        return f"Пользователь с логином {login} уже существует. Пожалуйста, выберите другой логин"

    # проверяем, что пароль достаточно сложный
    password_verdict = checking_password_complexity(password)
    if password_verdict is not None:
        return password_verdict

    # занос данных о пользователе в USERS
    query = "INSERT INTO users(login, password, name, email) VALUES(?, ?, ?, ?)"
    cursor.execute(query, (login, password, name, email))
    connection.commit()
    return None


def authentication(login, password, re_password):
    # проверка на совпадение паролей
    if password != re_password:
        return "Введённые пароли не совпадают"

    # смотрим, есть ли кортеж в USERS, где login и password данные
    query = "SELECT password FROM USERS WHERE login=? AND password=?"
    result = cursor.execute(query, (login, password)).fetchall()
    if len(result) == 0:
        return "Неправильный логин или пароль"
    return None


def change_password(login, old_password, new_password):
    # проверка на то, что старый и новый пароли различны
    if old_password == new_password:
        return "Вы указали один и тот же пароль"

    # проверяем новый пароль на надежность
    password_verdict = checking_password_complexity(new_password, True)
    if password_verdict is not None:
        return password_verdict

    # проверяем, что старый пароль верный
    if not authentication(login, old_password, old_password) is None:
        return "Вы указали неверный старый пароль"

    # обновляем данные в USERS
    query = "UPDATE USERS SET password=? WHERE login=?"
    cursor.execute(query, (new_password, login,))
    connection.commit()
    return None


def change_name(login, name):
    # обновляем данные в БД
    query = "UPDATE USERS SET name=? WHERE login=?;"
    cursor.execute(query, (name, login,))
    connection.commit()
    return None


def delete_login(login):
    # обновляем данные в БД
    query = "DELETE from USERS WHERE login=?"
    cursor.execute(query, (login,))
    connection.commit()
    return None


def get_users_list():
    query = "SELECT login FROM USERS"
    res = cursor.execute(query).fetchall()
    return res

# функции для работы с консолью
def print_red(text):
    print("\033[31m{}".format(text))


def print_yellow(text):
    print("\033[33m{}".format(text))


def print_green(text):
    print("\033[32m{}".format(text))


def print_white(text):
    print("\033[38m{}".format(text))

# функции для вывода ошибок
def error_in_command():
    print_red("ОШИБКА >>> НЕИЗВЕСТНАЯ КОМАНДА")


def blocked_command():
    print_red("ОШИБКА >>> НЕДОПУСТИМАЯ КОМАНДА")


def error_in_arguments():
    print_red("ОШИБКА >>> НЕВЕРНОЕ КОЛИЧЕСТВО АРГУМЕНТОВ")


# данные пользователя
LOGIN = "Can4k"
isAppClose = False

# Приложение
print_white("\nCan4k's application is ready to work...")
print_yellow("Введите /help для получения справки")

while True:
    # Если нужно закрыть приложение
    if isAppClose:
        break

    inp = input().split()
    match inp[0]:
        case ("/help"):
            if len(inp) > 1:
                # неверное количество аргументов
                error_in_arguments()
            else:
                # выводим помощь
                print_yellow(">>> Квадратные скобки писать не надо <<<")
                if len(LOGIN):
                    print_white("/change_password [пароль] [новый пароль] -> сменить пароль")
                    print_white("/change_name [новое имя] -> сменить имя")
                    print_white("/delete -> удалить личный кабинет")
                    print_white("/leave -> выйти из личного кабинета")
                    print_white("/users_list -> вывести список пользователей")
                else:
                    print_white("/register [логин] [пароль] [имя] [email] -> зарегистрироваться в системе")
                    print_white("/auth [логин] [пароль] [повтор пароля] -> войти в личный кабинет")
                print_white("/close -> закрыть приложение")
        case "/close":
            isAppClose = True
        case "/auth":
            if len(LOGIN):
                # команда не может быть выполнена
                blocked_command()
            else:
                if len(inp) != 4:
                    # неверное количество аргументов
                    error_in_arguments()
                else:
                    # пытаемся выполнить аунтетификацию
                    verdict = authentication(inp[1], inp[2], inp[3])
                    if verdict is None:
                        print_green("Вы зашли в свой кабинет")
                        LOGIN = inp[1]
                    else:
                        print_red("ОШИБКА >>> " + verdict)
        case "/register":
            if len(LOGIN):
                # команда не может быть выполнена
                blocked_command()
            else:
                if len(inp) != 5:
                    # неверное количество аргументов
                    error_in_arguments()
                else:
                    # пытаемся выполнить регистрацию
                    verdict = registration(inp[1], inp[2], inp[3], inp[4])
                    if verdict is None:
                        print_green("Успешная регистрация")
                    else:
                        print_red("ОШИБКА >>> " + verdict)
        case "/change_password":
            if not len(LOGIN):
                # команда не может быть выполнена
                blocked_command()
            else:
                if len(inp) != 3:
                    # неверное количество аргументов
                    error_in_arguments()
                else:
                    # пытаемся выполнить изменение пароля
                    verdict = change_password(LOGIN, inp[1], inp[2])
                    if verdict is None:
                        print_green("Пароль успешно изменен")
                    else:
                        print_red("ОШИБКА >>> " + verdict)
        case "/change_name":
            if not len(LOGIN):
                # команда не может быть выполнена
                blocked_command()
            else:
                if len(inp) != 2:
                    # неверное количество аргументов
                    error_in_arguments()
                else:
                    # меняем имя
                    change_name(LOGIN, inp[1])
                    print_green("Имя успешно изменено")
        case "/delete":
            if not len(LOGIN):
                # команда не может быть выполнена
                blocked_command()
            else:
                if len(inp) != 1:
                    # неверное количество аргументов
                    error_in_arguments()
                else:
                    # удаляем аккаунт, выполняем выход
                    delete_login(LOGIN)
                    print_green("Личный кабинет удален")
                    print_yellow("Выход из личного кабинета")
                    LOGIN = ""
        case "/leave":
            if not len(LOGIN):
                # команда не может быть выполнена
                blocked_command()
            else:
                # выполняем выход
                LOGIN = ""
                print_yellow("Выход из личного кабинета")
        case "/users_list":
            if not len(LOGIN):
                # команда не может быть выполнена
                blocked_command()
            else:
                # выполняем вывод
                for i in list(get_users_list()):
                    if i[0] == LOGIN:
                        print_green(i[0])
                    else:
                        print_white(i[0])
        case _:
            error_in_command()

connection.close()
