import os
import argparse
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from requests import HTTPError
from urllib.parse import urljoin, urlsplit
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.status_code == 302 or response.status_code == 301:
        raise HTTPError


def get_download_url(response):
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        url = soup.find('a', string="скачать txt")['href']
    except:
        print('Нет книги')
    download_url = urljoin('https://tululu.org/', url)
    return download_url


def parse_book_page(response):
    book_comments = []
    book_category = []
    soup = BeautifulSoup(response.text, 'lxml')

    name_book, author = soup.find('h1').text.split('::')
    name_book = name_book.strip()
    author = author.strip()

    comments = soup.find_all(class_="texts")
    for comment in comments:
        soup_comment = BeautifulSoup(str(comment), 'lxml')
        text_comment = soup_comment.find(class_="black")
        book_comments.append(text_comment.text)

    categories = soup.find_all('span', class_="d_book")
    soup_category = BeautifulSoup(str(categories), 'lxml')
    check = soup_category.find_all('a')
    for category in check:
        book_category.append(category.contents[0])

    info_book = {'name_book': name_book, 'author': author, 'comments': book_comments, 'category': book_category}
    return info_book


def download_img(url, folder):

    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()

    Path(folder).mkdir(parents=True, exist_ok=True) 
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        check_for_redirect(response)
        url = soup.find(class_="bookimage").find('a').find('img')['src']
        img_url = urljoin('https://tululu.org/', url)

        response_download = requests.get(img_url, allow_redirects=False)
        response_download.raise_for_status()
        check_for_redirect(response_download)
        url = urlsplit(url)
        name_img = url.path.split('/')[-1]
        filepath = os.path.join(folder, name_img)
        with open(filepath, 'wb') as file:
            file.write(response_download.content)
    except:
        print('Нет изображения')


def download_txt(url, number_book, folder):
    Path(folder).mkdir(parents=True, exist_ok=True) 
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()

    try:
        check_for_redirect(response)
        book_page = parse_book_page(response)
        name_book = book_page['name_book']
        author = book_page['author']
        path_book = sanitize_filename(f'{number_book}. {name_book}.txt')
        try:
            download_url = get_download_url(response)
            response_download = requests.get(download_url, allow_redirects=False)
            response_download.raise_for_status()
            check_for_redirect(response_download)
            filepath = os.path.join(folder, path_book)

            with open(filepath, 'wb') as file:
                file.write(response_download.content)

            print(f'Название: {name_book}')
            print(f'Автор: {author}')
            print(' ')
        except:
            print('Error')

    except HTTPError:
        print('Ошибка 302')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Программа скачивает книги с сайта tululu.org')
    parser.add_argument('start_id', help='Число с какой книги начинать', type=int, default=1)
    parser.add_argument('end_id', help='Число до какой страницы закончить', type=int, default=11)
    args = parser.parse_args()
    for number_book in range(args.start_id, args.end_id):
        download_txt(f'https://tululu.org/b{number_book}/', number_book, folder='books/')
        download_img(f'https://tululu.org/b{number_book}/', folder='images/')