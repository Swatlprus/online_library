import os
import requests
from pathvalidate import sanitize_filename
from pathlib import Path
from bs4 import BeautifulSoup
from requests import HTTPError


def get_download_url(response):
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        url = soup.find('a', string="скачать txt")['href']
    except:
        print('Нет книги')
    download_url = 'https://tululu.org/' + url
    return download_url


def get_name_book(response):
    soup = BeautifulSoup(response.text, 'lxml')
    name_book, author = soup.find('h1').text.split('::')
    return name_book.strip()


def check_for_redirect(response):
    if response.status_code == 302 or response.status_code == 301:
        raise HTTPError


def download_txt(url, id, folder='books/'):
    Path(folder).mkdir(parents=True, exist_ok=True) 
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()

    try:
        check_for_redirect(response)
        name_book = sanitize_filename(f'{id}. {get_name_book(response)}.txt')
    
        try:
            download_url = get_download_url(response)
            response_download = requests.get(download_url, allow_redirects=False)
            response_download.raise_for_status()
            check_for_redirect(response_download)

            filepath = os.path.join(folder, name_book)
            with open(filepath, 'wb') as file:
                file.write(response_download.content)
        except:
            print('Error')

    except HTTPError:
        print('Ошибка 302')


if __name__ == "__main__":
    for id in range(1, 11):
	    download_txt(f'https://tululu.org/b{id}/', id, folder='books/')
        # download_txt(f'http://tululu.org/txt.php?id={id}/', folder='books/')