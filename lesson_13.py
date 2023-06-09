import requests
import bs4
import json
from datetime import datetime

# Страница с курсами валют установленными ЦБ.
CB_SITE_URL = 'https://www.cbr.ru/currency_base/daily/'


class ParserCBRF:
    @staticmethod
    def _get_html() -> str:
        """
        Получает код страницы.
        """
        response = requests.get(url=CB_SITE_URL)
        return response.content.decode()

    @staticmethod
    def _parse_html(html: str) -> dict:
        """
        Парсит содержимое страницы в словарь.
        """
        soup = bs4.BeautifulSoup(html, 'html.parser')
        # получает таблицу с курсами
        table = soup.find('table', {'class': 'data'}).find('tbody')
        # получает строки таблицы, исключая первую (пустую)
        rows = table.find_all('tr')[1:]
        # построчно парсит таблицу
        data = {}
        for row in rows:
            columns = row.find_all('td')
            # получает содержимое колонок
            columns = [column.text for column in columns]
            #
            ticker = columns[1]
            count = columns[2]
            name = columns[3]
            rate = columns[4]
            # сохраняет колонки в словарь
            data[ticker] = {'count': count,
                            'name': name,
                            'rate': rate}
        return data

    @staticmethod
    def _print_data(data: dict) -> None:
        """
        Печатает результат парсинга.
        """
        for ticker, d in data.items():
            print(f"{d['count']} {d['name']} ({ticker}) стоит {d['rate']} рублей.")

    @staticmethod
    def _save_data(data: dict) -> None:
        """
        Сохраняет результат парсинга в файл.
        """
        with open(f"Курсы валют от {datetime.now().strftime('%d.%m.%Y')}.json", 'w') as f:
            json.dump(data, f)

    def start(self) -> None:
        """
        Парсинг курсов валют с сайта ЦБ.
        """
        html = self._get_html()
        data = self._parse_html(html=html)
        self._print_data(data=data)
        self._save_data(data=data)


if __name__ == '__main__':
    parser = ParserCBRF()
    parser.start()
