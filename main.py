import os
import sys
import time
import argparse
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit
from pathvalidate import sanitize_filename
from requests import HTTPError, ConnectionError

class BookNameError(AttributeError):
    pass

class BookUrlError(AttributeError):
    pass

def check_for_redirect(response):
    if response.history:
        raise HTTPError
    

def parse_book_page(response, url):
    book_comments = []
    book_categories = []
    soup = BeautifulSoup(response.text, 'lxml')

    try:
        book_name, author = soup.find('h1').text.split('::')
        book_name = book_name.strip()
        author = author.strip()
    except AttributeError:
        raise BookNameError()

    try:
        book_url = soup.find('a', string="скачать txt")['href']
        download_url = urljoin(url, book_url)
    except TypeError:
        raise BookUrlError()

    img_url = soup.find(class_="bookimage").find('a').find('img')['src']
    book_img_url = urljoin(url, img_url)

    comments = soup.find_all(class_="texts")
    book_comments = [comment.span.text for comment in comments]

    categories = soup.find('span', class_="d_book").find_all('a')
    book_categories = [category.text for category in categories]
    
    page_book = {'book_name': book_name, 'author': author, 'download_url': download_url, 'book_img': book_img_url, 'comments': book_comments, 'categories': book_categories}
    return page_book


def download_img(url, book_img_url, folder):
    Path(folder).mkdir(parents=True, exist_ok=True) 

    response = requests.get(book_img_url, allow_redirects=False)
    response.raise_for_status()
    check_for_redirect(response)

    url = urlsplit(book_img_url)
    img_name = url.path.split('/')[-1]
    filepath = os.path.join(folder, img_name)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def download_txt(book_number, book_name, download_url, folder='books/'):
    Path(folder).mkdir(parents=True, exist_ok=True) 
    path_book = sanitize_filename(f'{book_number}. {book_name}.txt')

    response = requests.get(download_url, allow_redirects=False)
    response.raise_for_status()
    check_for_redirect(response)

    filepath = os.path.join(folder, path_book)

    with open(filepath, 'wb') as file:
        file.write(response.content)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Программа скачивает книги с сайта tululu.org')
    parser.add_argument('start_id', help='Число с какой книги начинать', type=int, default=1)
    parser.add_argument('end_id', help='Число до какой страницы закончить', type=int, default=11)
    args = parser.parse_args()
    for book_number in range(args.start_id, args.end_id):
        url = f'https://tululu.org/b{book_number}/'
        try:
            response = requests.get(url, allow_redirects=False)
            response.raise_for_status()
            check_for_redirect(response)

            book_page = parse_book_page(response, url)
            book_name = book_page['book_name']
            author = book_page['author']
            categories = book_page['categories']
            download_url = book_page['download_url']
            book_img_url = book_page['book_img']

            download_book = download_txt(book_number, book_name, download_url, folder='books/')
            download_img(url, book_img_url, folder='images/')
            print(f'Книга со страницы {book_number} скачана')
        except HTTPError as err:
            print(err.__str__(), file=sys.stderr)
            print('HTTPError')
            print('Данной ссылки не существует')
        except BookNameError as err:
            print(f'Название книги не найденно на странице. Номер страницы {book_number}')
        except BookUrlError as err:
            print(f'Нет ссылки для скачивания книги. Номер страницы {book_number}')
        except ConnectionError as err:
            print(err.__str__(), file=sys.stderr)
            print('ConnectionError')
            print('Ошибка: Разрыв связи')
            time.sleep(10)