# Парсим онлайн-библиотеку

Данный проект парсит и скачивает книги с сайта [tululu.org](https://tululu.org/).

## Требования

Должно быть установлены следующее ПО:

- [Python 3.x](https://www.python.org/)
- Виртуальное окружение

## Как установить

Скопируйте репозиторий удобным для вас способом.

Создайте виртуальное окружение.

Используйте `pip` для установки зависимостей:

```shell
pip install -r requirements.txt
```

## Запуск функции main.py

Скрипт принимает на вход две числовые переменные: начало и конец. Которые определяют с какого по какое число будет парситься сайт. Значения по умолчания 1 и 11 - скачает книги с 1-ой по 10-ой включительно. Пример запуска:

```shell
python3 main.py 12 25
```
## Что должны получить от main.py

Программа создат две папки: books - туда поместить скачанные книги в формате .txt и папку images - туда поместить скачанные обложки данных книг.

## Запуск функции parse_tululu_category.py

Скрипт скачивает книги с категории Фантастика. Имеет несколько аргументов запуска:
```
--start_page - С какой страницы начинает скачивать книги
--end_page - До какой страницы скачивает книги
--dest_folder - Путь к каталогу с результатами парсинга: картинкам, книгам, JSON
--skip_imgs - Не скачивать изображения
--skip_txt - Не скачивать книги
--json_path - Путь к *.json результатам
```

Которые определяют с какого по какое число будет парситься сайт. Значения по умолчания 1 и 11 - скачает книги с 1-ой по 10-ой включительно. Пример запуска:

```shell
python3 parse_tululu_category.py --start_page 5 --end_page 15
```

Данный код скачает книги с 5 по 15 страницы (не включительно)

## Что должны получить от parse_tululu_category.py

Программа создат две папки: books - туда поместить скачанные книги в формате .txt и папку images - туда поместить скачанные обложки данных книг. При условии, что аргументы запуска вы не меняли.

## Цели проекта

Учебный проект по парсингу онлайн-библиотеки от онлайн-курса Devman (dvmn.org) ([dvmn.org](https://dvmn.org/)).
