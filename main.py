import os
import time
import argparse
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from requests import HTTPError, ConnectionError
from urllib.parse import urljoin, urlsplit
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def get_download_url(url):
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book_url = soup.find('a', string="скачать txt")['href']
    download_url = urljoin(url, book_url)
    return download_url


def parse_book_page(response):
    book_comments = []
    book_category = []
    soup = BeautifulSoup(response.text, 'lxml')

    book_name, author = soup.find('h1').text.split('::')
    book_name = book_name.strip()
    author = author.strip()

    img_url = soup.find(class_="bookimage").find('a').find('img')['src']
    book_img_url = urljoin(url, img_url)

    comments = soup.find_all(class_="texts")
    for comment in comments:
        soup_comment = BeautifulSoup(str(comment), 'lxml')
        text_comment = soup_comment.find(class_="black")
        book_comments.append(text_comment.text)

    categories = soup.find_all('span', class_="d_book")
    soup_category = BeautifulSoup(str(categories), 'lxml')
    links_categories = soup_category.find_all('a')
    for category in links_categories:
        book_category.append(category.text)

    page_book = {'book_name': book_name, 'author': author, 'book_img': book_img_url, 'comments': book_comments, 'category': book_category}
    return page_book


def download_img(url, book_page, folder):
    Path(folder).mkdir(parents=True, exist_ok=True) 

    book_img_url = book_page['book_img']
    response_download = requests.get(book_img_url, allow_redirects=False)
    response_download.raise_for_status()
    check_for_redirect(response_download)

    url = urlsplit(book_img_url)
    img_name = url.path.split('/')[-1]
    filepath = os.path.join(folder, img_name)
    with open(filepath, 'wb') as file:
        file.write(response_download.content)


def download_txt(url, book_number, book_page, folder):
    Path(folder).mkdir(parents=True, exist_ok=True) 

    book_name = book_page['book_name']
    author = book_page['author']
    category = book_page['category']
    path_book = sanitize_filename(f'{book_number}. {book_name}.txt')

    download_url = get_download_url(url)
    response_download = requests.get(download_url, allow_redirects=False)
    response_download.raise_for_status()
    check_for_redirect(response_download)

    filepath = os.path.join(folder, path_book)

    with open(filepath, 'wb') as file:
        file.write(response_download.content)

    print(f'Название: {book_name}')
    print(f'Автор: {author}')
    print(f'Категория: {category}')
    print(' ')

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
            book_page = parse_book_page(response)
            download_txt(url, book_number, book_page, folder='books/')
            download_img(url, book_page, folder='images/')
        except HTTPError:
            print('HTTPError')
            print(' ')
        except AttributeError:
            print('AttributeError')
            print(' ')
        except ConnectionError:
            print('ConnectionError')
            time.sleep(5)
            try:
                book_page = parse_book_page(url)
                download_txt(url, book_number, book_page, folder='books/')
                download_img(url, book_page, folder='images/')
            except ConnectionError:
                print(ConnectionError)
        except:
            print('Error')
            print(' ')