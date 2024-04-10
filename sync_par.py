import requests
import dotenv
import re
import time

from typing import NamedTuple
from bs4 import BeautifulSoup


class myException(Exception):
    pass


def check(response: requests.Response):
    if response.status_code != 200:
        raise myException(f'status={response.status_code}')


class Book(NamedTuple):
    name: str
    link: str

def main():
    books = []
    with requests.Session() as ses:
        root = dotenv.dotenv_values()['URL']
        res_root = ses.get(root)
        check(res_root)
        soup_root = BeautifulSoup(res_root.text, 'lxml')
        len_ = int(soup_root.findAll(class_='nums')[-1].text.replace('\n', '')[-1])
        for page in range(1, len_ + 1):
            print(page)
            url = f'{root}{dotenv.dotenv_values()['PAGE']}{page}'
            response = ses.get(url)
            check(response)
            soup = BeautifulSoup(response.text, 'lxml')
            data = [info.findAll('h3')for info in soup.findAll(class_='block')]
            for book in data:
                name = re.sub('\n+\t+', '', book[0].text)
                name = re.sub('\t+', ' ', name)
                link = book[0].find('a').get('href')
                b = Book(name=name, link=link)
                books.append(b)
    print(books)

if __name__ == '__main__':
    start = time.time()
    main()
    print(time.time()-start)