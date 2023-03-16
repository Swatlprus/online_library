import os
import sys
import time
import json
import argparse
import requests
from bs4 import BeautifulSoup
from requests import HTTPError
from urllib.parse import urljoin
from main import parse_book_page, download_txt, download_img, check_for_redirect, BookNameError, BookUrlError


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Программа скачивает книги с сайта tululu.org')
    parser.add_argument('--start_page', help='Число с какой страницы начинать', type=int, default=1)
    parser.add_argument('--end_page', help='Число до какой страницы закончить', type=int, default=1000)
    parser.add_argument('--dest_folder', help='Путь к каталогу с результатами парсинга: картинкам, книгам, JSON.', default='./')
    parser.add_argument('--skip_imgs', help='Не скачивать картинки', action='store_false')
    parser.add_argument('--skip_txt', help='Не скачивать книги', action='store_false')
    parser.add_argument('--json_path', help='Указать свой путь к *.json файлу с результатами', default='./books.json')
    args = parser.parse_args()
    books = []
    books_url = []
    for page_number in range(args.start_page, args.end_page):
        url = f'https://tululu.org/l55/{page_number}'
        response = requests.get(url, allow_redirects=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        check_for_redirect(response)
        books_id = soup.select('.d_book')
        for book_id in books_id:
            books_url.append(urljoin(url, book_id.a['href']))

    for book_number, book_url in enumerate(books_url, start=1):
        try:
            response = requests.get(book_url, allow_redirects=False)
            response.raise_for_status()
            check_for_redirect(response)

            book_page = parse_book_page(response, book_url)
            title = book_page['title']
            author = book_page['author']
            genres = book_page['genres']
            comments = book_page['comments']
            download_url = book_page['download_url']
            book_img_url = book_page['book_img_url']

            if not args.skip_txt:
                path_books = os.path.join(args.dest_folder, 'books/')
                book_path = download_txt(book_number, title, download_url, folder=path_books)
            else:
                book_path = None
            if not args.skip_imgs:
                path_images = os.path.join(args.dest_folder, 'images/')
                img_src = download_img(url, book_img_url, folder=path_images)
            else:
                img_src = None

            if book_path:
                page_book = {"title": title, "author": author, "img_src": img_src, "book_path": book_path, "comments": comments, "genres": genres}
                books.append(page_book)

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

    books_json = json.dumps(books, ensure_ascii=False)
    with open(os.path.join(args.dest_folder, args.json_path), "w+", encoding='utf8') as my_file:
        my_file.write(books_json)