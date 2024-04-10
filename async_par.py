import asyncio
import aiohttp
import dotenv
import re
import time

from typing import NamedTuple
from bs4 import BeautifulSoup

class myException(Exception):
    pass

async def check(response: aiohttp.ClientResponse):
    if response.status != 200:
        raise myException(f'status={response.status}')

class Book(NamedTuple):
    name: str
    link: str

async def fetch_page(session, root, page):
    url = f'{root}{dotenv.dotenv_values()["PAGE"]}{page}'
    async with session.get(url, ssl=False) as response:
        await check(response)
        soup = BeautifulSoup(await response.text(), 'lxml')
        data = [info.findAll('h3') for info in soup.findAll(class_='block')]
        return [Book(name=re.sub('\n+\t+', '', book[0].text), link=book[0].find('a').get('href')) for book in data]

async def main():
    root = dotenv.dotenv_values()['URL']
    async with aiohttp.ClientSession() as ses:
        async with ses.get(root, ssl=False) as res_root:
            await check(res_root)
            soup_root = BeautifulSoup(await res_root.text(), 'lxml')
            len_ = int(soup_root.findAll(class_='nums')[-1].text.replace('\n', '')[-1])
            tasks = [fetch_page(ses, root, page) for page in range(1, len_ + 1)]
            books_list = await asyncio.gather(*tasks)
            books = [book for sublist in books_list for book in sublist]
    print(books)

if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)