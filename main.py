from time import sleep
import re
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import json
import pprint


def get_headers():
    headers = Headers(browser='firefox', os='win')
    return headers.generate()


def get_response(n):
    HOST = f'https://spb.hh.ru/search/vacancy?text=Python&salary=&area=1&area=2&ored_clusters=true&enable_snippets=true&page={n}'
    response = requests.get(HOST, headers=get_headers())
    hh_main = response.text
    if response.status_code == 200:
        return hh_main
    else:
        return False


pattern1 = f'([Ff]lask)'
pattern2 = f'([Dd]jango)'
count = 0
run = True
parced = []

while run:
    sleep(1)
    content = get_response(count)
    if content:
        soup = BeautifulSoup(content, features='lxml')
        main_content = soup.find('div', id="a11y-main-content")
        vacanceses = main_content.findAll('div', class_='vacancy-serp-item__layout')

        for vacancy in vacanceses:
            info = vacancy.find('div', class_='g-user-content').findAll('div', class_='bloko-text')
            desc = []
            for i in info:
                desc.append(i.text)
            str_ = ', '.join(desc)
            find_1 = re.findall(pattern1, str_)
            find_2 = re.findall(pattern2, str_)
            if len(find_1) and len(find_2):
                link = vacancy.find('a')['href']
                try:
                    salary = vacancy.find('span', class_='bloko-header-section-3').text.replace('\u202f', ' ')
                except:
                    salary = None
                company_name = vacancy.find('a', class_='bloko-link bloko-link_kind-tertiary').text
                city = vacancy.find('div', {'data-qa': "vacancy-serp__vacancy-address", 'class': 'bloko-text'}).text
                print(
                    f'Найдено на листе: {count + 1} link:{link}, salary:{salary}, company:{company_name}, city:{city}')
                data = dict()
                data['link'] = link
                data['salary'] = salary
                data['company_name'] = company_name
                data['city'] = city
                print(f'Словарь сформирован {data}')
                parced.append(data)
                print('Добавлено в список')

        count += 1
    else:
        run = False

with open('result.json', 'w', encoding='utf-8') as file:
    json.dump(parced, file, ensure_ascii=False, indent=4)
    print('Записано в файл result.json')


pprint.pprint(parced)
