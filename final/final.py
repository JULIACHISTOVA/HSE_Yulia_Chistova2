import requests
import bs4
import json
from datetime import datetime, date, timedelta
from decimal import Decimal
from pathlib import Path

SITE_URL = 'https://www.cbr.ru/hd_base/ProcStav/IRB_OMMIR/?UniDbQuery.Posted=True&UniDbQuery.From={}&UniDbQuery.To={}'


class ParserCBRF:
    @staticmethod
    def _get_html(date_from: date, date_to: date) -> str:
        """
        Получает код страницы.
        """
        response = requests.get(url=SITE_URL.format(date_from.strftime('%d.%m.%Y'), date_to.strftime('%d.%m.%Y')))
        return response.content.decode()

    @staticmethod
    def _parse_html(html: str) -> dict:
        """
        Парсит содержимое страницы в словарь.
        """
        soup = bs4.BeautifulSoup(html, 'html.parser')
        # получает таблицу с курсами
        table = soup.find('table', {'class': 'data spaced'})
        # получает строки таблицы, исключая первую (пустую)
        rows = table.find_all('tr')[2:]
        # построчно парсит таблицу
        data = {}
        for row in reversed(rows):
            columns = row.find_all('td')
            # получает содержимое колонок
            columns = [column.text for column in columns]
            # сохраняет колонки в словарь
            day_date = datetime.strptime(columns[0], '%d.%m.%Y').date()
            data_row = {'key_rate': columns[1],
                        'lower_limit_deposits': columns[2],
                        'upper_limit_repo': columns[3],
                        'upper_limit_credits': columns[4],
                        'miacr': columns[5],
                        'ruonia': columns[6]}
            # парсинг значений колонок
            data_row = {k: None if v == ' — ' else Decimal(v.replace(',', '.')) for k, v in data_row.items()}
            #
            data[day_date] = data_row
        return data

    @staticmethod
    def _saturate_data(data: dict) -> dict:
        """
        Делает данные непрерывными (заполняет выходные дни).
        """
        date_from = list(data.keys())[0]  # дата первого значения
        date_to = list(data.keys())[-1]  # дата последнего значения
        #
        data_saturated = {}
        last_data = data[date_from]
        day_date = date_from
        # Если за день нет данных, то подставляет данные за предыдущий день.
        while day_date < date_to + timedelta(days=1):
            data_saturated[day_date] = data.get(day_date, last_data)
            last_data = data_saturated[day_date]
            #
            day_date += timedelta(days=1)
        return data_saturated

    @staticmethod
    def _serialize_data(data: dict) -> dict:
        """
        Сериализует значения словаря в строки.
        """
        data_serialized = {}
        for day_date, day_data in data.items():
            data_serialized[day_date.isoformat()] = {k: str(v) for k, v in day_data.items()}
        return data_serialized

    @staticmethod
    def _save_data(data: dict) -> None:
        """
        Сохраняет результат парсинга в файл.
        """
        with open(Path('parsed_data') / Path('Процентный коридор.json'), 'w') as f:
            json.dump(data, f)

    def start(self) -> None:
        """
        Парсинг "Процентный коридор Банка России и ставки сегмента овернайт денежного рынка" с сайта ЦБ за год.
        """
        # крайние даты за год от сегодняшнего дня
        date_today = datetime.now().date()
        date_from = date_today - timedelta(days=365)
        # Получает код страницы.
        html = self._get_html(date_from=date_from,
                              date_to=date_today)
        # Парсит содержимое страницы в словарь.
        data = self._parse_html(html=html)
        # Делает данные непрерывными (заполняет выходные дни).
        data_saturated = self._saturate_data(data=data)
        # Сериализует значения словаря в строки.
        data_serialized = self._serialize_data(data=data_saturated)
        # Сохраняет результат парсинга в файл.
        self._save_data(data=data_serialized)


class DataBaseCBRF:
    """
    Выводит сохранённые данные.
    """
    def __init__(self):
        self._data = None

    def read_data(self, filename: str) -> None:
        """
        Читает результаты парсинга из файла.
        """
        with open(Path('parsed_data') / Path(f'{filename}.json')) as file:
            self._data = json.load(file)

    def get_value_by_date(self, value_name: str, day_date: date) -> str:
        """
        Возвращает значение параметра за указанную дату.
        """
        try:
            data_by_date = self._data[day_date.isoformat()]
        except KeyError:
            return 'Нет данных за указанную дату.'
        #
        try:
            return data_by_date[value_name]
        except KeyError:
            return 'Неверное имя параметра.'

    def get_value_last(self, value_name: str) -> str:
        """
        Возвращает последнее известное значение параметра.
        """
        try:
            return list(self._data.values())[-1][value_name]
        except KeyError:
            return 'Неверное имя параметра.'

    def get_values_by_range(self, value_name: str, date_from: date, date_to: date) -> list:
        """
        Возвращает значение параметра за диапазон дат.
        """
        values_by_range = []
        day_date = date_from
        while day_date < date_to + timedelta(days=1):
            values_by_range.append(self.get_value_by_date(value_name=value_name, day_date=day_date))
            #
            day_date += timedelta(days=1)
        return values_by_range


if __name__ == '__main__':
    parser = ParserCBRF()
    parser.start()
    #
    database = DataBaseCBRF()
    database.read_data(filename='Процентный коридор')
    #
    print(database.get_value_by_date(value_name='lower_limit_deposits',
                                     day_date=datetime(day=10, month=6, year=2023).date()))
    print(database.get_value_last(value_name='upper_limit_repo'))
    print(database.get_values_by_range(value_name='upper_limit_credits',
                                       date_from=datetime(day=1, month=5, year=2023).date(),
                                       date_to=datetime(day=9, month=5, year=2023).date()))
