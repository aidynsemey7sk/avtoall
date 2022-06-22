import multiprocessing
import time
import multiprocessing as mp
from bs4 import BeautifulSoup
import requests

URL = 'https://www.avtoall.ru/'

html = requests.get(URL)
status = html.status_code


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
                        print(rubric)
                        all_rubrics.append(rubric)

        else:
            print('Что то с сайтом')
        return all_rubrics

    def get_all_categories_for_rubric(self, link_for_rubric):
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

    def get_pages_for_category(self, link_for_category):
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

    def parse(self, data):
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
                    if type(tag) != int:
                        link = URL + tag[1:]
                        print(name, link)
                        result.append(
                            {
                                'name': name, 'link': link
                            }
                        )
                        time.sleep(3)
        print(len(result))


# av = AvtoAll(URL)
# rubr = av.get_all_rubrics()
# print(rubr)
# av.get_all_categories_for_rubric("/zapchasti_inomarki/")


# print(av.get_pages_for_category('/bmw/'))

# print(av.parse({'category_url': 'https://www.avtoall.ru/bmw/', 'all_page': 59}))
# category = av.get_all_categories_for_rubric("/zapchasti_inomarki/")
# for i in category:
#     category_obj = av.get_pages_for_category(i)
#     av.parse(category_obj)
#     time.sleep(5)
#     break

if __name__ == '__main__':

    count = 0
    avtoall = AvtoAll(URL)
    """Получим все рубрики"""
    rubrics = avtoall.get_all_rubrics()
    print(len(rubrics))
    res = []
    """Получим из каждой рубрики все категории"""
    for rub in rubrics:
        categories = avtoall.get_all_categories_for_rubric(rub)
        count += 1
        # print(count, categories)
        """Получим из каждой категории все страницы и количество страниц у каждой категории"""
        for category in categories:
            start_time = time.time()
            category_obj = avtoall.get_pages_for_category(category)
            print(category_obj)
            res.append(category_obj)
            """Парсим"""
            # avtoall.parse(category_obj)
            # print("--- %s seconds ---" % (time.time() - start_time))

            # with multiprocessing.Pool(multiprocessing.cpu_count() * 3) as p:
            #     p.map(avtoall.parse, res)





