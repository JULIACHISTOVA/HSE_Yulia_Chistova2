import json
import re


def execute_task_1():
    """Задание 1."""
    # a. Чтение списка ИНН трейдеров для поиска.
    with open('traders.txt') as file:
        lines = file.readlines()
    # очистка строк от спецсимвола окончания строки
    traders_inn = []
    for line in lines:
        traders_inn.append(line.strip())
    # b. Чтение данных трейдеров.
    with open('traders.json') as file:
        traders_data_list = json.load(file)
    # запись данных трейдеров в словарь для поиска по ИНН
    traders_data_dict = {}
    for trader_data in traders_data_list:
        traders_data_dict[trader_data['inn']] = trader_data
    # Поиск трейдеров в базе по ИНН.
    traders_found = []
    for trader_inn in traders_inn:
        traders_found.append(traders_data_dict[trader_inn])
    # c. Запись данных найденных трейдеров в csv файл.
    with open('traders.csv', 'w') as file:
        for trader_data in traders_found:
            file.write('{inn};{ogrn};{address}\n'.format(**trader_data))


def find_emails_in_text(text):
    """Поиск email в тексте."""
    return re.findall(r'\\s([\\w._$+~-]+@[a-z]+\.[a-z]+)(?:\\s|$|,|\.)', text)


def execute_task_2():
    """Задание 2."""
    # Чтение данных банкротов.
    with open('1000_efrsb_messages.json') as file:
        data = json.load(file)
    #
    bankrupts_emails = {}
    for bankrupt in data:
        # Поиск email в тексте сообщения.
        emails_in_msg = find_emails_in_text(bankrupt['msg_text'])
        # * Поиск email во всех данных.
        # конвертация словаря с данными банкрота в текст
        bankrupt_text = json.dumps(bankrupt)
        emails_in_all_data = find_emails_in_text(bankrupt_text)
        # добавление email в словарь
        bankrupts_emails[bankrupt['publisher_inn']] = list(set(emails_in_msg + emails_in_all_data))
    # Запись результатов поиска в файл.
    bankrupts_emails_json = json.dumps(bankrupts_emails)
    with open('emails.json', 'w') as file:
        file.write(bankrupts_emails_json)


if __name__ == '__main__':
    execute_task_1()
    execute_task_2()
