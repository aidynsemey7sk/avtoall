import time
from bs4 import BeautifulSoup
import requests

URL = 'https://www.avtoall.ru/'

html = requests.get(URL)
status = html.status_code

Red = "\033[31m"
Yellow = "\033[33m"
Green = "\033[32m"
reset = '\033[0m'


class AvtoAll:

    def __init__(self, url):
        self.url = url
        self.main_page = url

    def get_all_rubrics(self) -> list:
        all_rubrics = []
        html = requests.get(self.url)
        soup = BeautifulSoup(html.text, features="html.parser")
        if html.status_code == 200:
            mydivs = soup.find('ul', id="main_top_sections")
            for li in mydivs:
                tag = li.find('a')
                if type(tag) != int:
                    if tag.get('rel'):
                        rubric = tag.get('href')
                        all_rubrics.append(rubric)

        else:
            print('Что то с сайтом')
        return all_rubrics

    def get_all_categories_for_rubric(self, link_for_rubric: str) -> list:
        all_categoryes_for_rubric = []
        rubric_url = URL + link_for_rubric[1:]
        rubric_page = requests.get(rubric_url)
        if rubric_page.status_code == 200:
            soup = BeautifulSoup(rubric_page.text, features="html.parser")
            mydivs = soup.find(class_='subsections')
            for a in mydivs:
                tag = a.find('a')
                if type(tag) != int:
                    all_categoryes_for_rubric.append(tag.get('href'))
        return all_categoryes_for_rubric

    def get_pages_for_category(self, link_for_category: str) -> dict:
        all_car_spare_parts = []
        category_url = URL + link_for_category[1:]

        category_page = requests.get(category_url)
        all_page = 0
        if category_page.status_code == 200:
            soup = BeautifulSoup(category_page.text, features="html.parser")
            try:
                pager = soup.find(class_='pager')
            except:
                return {'category_url': category_url, 'all_page': all_page + 1}
            try:
                if pager:
                    all_page = pager.find(class_='last').find('a').get('href')
                    all_page = int(all_page.split('=')[-1])
                    return {'category_url': category_url, 'all_page': all_page}
            except Exception:
                return {'category_url': category_url, 'all_page': all_page + 1}

            return {'category_url': category_url, 'all_page': all_page}

    def parse(self, data: dict) -> list:
        category_url = data['category_url']
        all_page = data['all_page'] + 1
        result = []
        for i in range(all_page):
            if all_page == 0:
                category_page = requests.get(category_url)
            else:
                category_page = requests.get(category_url + f'?page={i}')
            if category_page.status_code == 200:
                soup = BeautifulSoup(category_page.text, features="html.parser")
                items = soup.find(class_='list-compact')
                items = items.find_all(class_='item')
                for item in items:

                    tag = item.find('a').get('href')
                    name = item.find(class_='item-name').text
                    code = item.find('small').text
                    article = item.find('b').text
                    article = article.replace('все', '')
                    article = article.strip()
                    if type(tag) != int:
                        link = URL + tag[1:]
                        print(name, link, Red, code, reset, Green, article, reset)
                        result.append(
                            {
                                'name': name, 'link': link
                            }
                        )
        return result


if __name__ == '__main__':

    avtoall = AvtoAll(URL)
    """Получим все рубрики"""
    rubrics = avtoall.get_all_rubrics()
    """Получим из каждой рубрики все категории"""
    for rub in rubrics:
        categories = avtoall.get_all_categories_for_rubric(rub)
        """Получим из каждой категории все страницы и количество страниц у каждой категории"""
        for category in categories:
            start_time = time.time()
            category_obj = avtoall.get_pages_for_category(category)
            """Парсим"""
            avtoall.parse(category_obj)

