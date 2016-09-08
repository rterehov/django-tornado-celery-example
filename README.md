# Описание

Пример использования Django, Tornado и Celery совместно на синтетической задаче.

Пользователь вводит список URL в клиента (браузер), задает время начала выполнения задач, и отправляет это все на сервер.

Сервер принимает не более 5 задач и начинает выполнять их в фоновом режиме в заданное время.

Задачи парсят URL, достают оттуда заголовок, описание и картинку. Последняя скачивается на сервер.

С клиента пользователь может наблюдать за прогрессом выполнения каждой задачи (включая прогресс скачивания изображения), может остановить задачи в любое время.

## Стек технологий

Клиент: 
- jQuery, SockJS

Сервер:
- Django (интерфейс пользователя, API для получения статусов)
- Tornado (отправка клиентам состояний по задачам)
- Celery (бекенд для фоновых задач)
- Redis


## Установка и запуск

1. Python 2.7, sqlite3, redis, пакеты для aptitude см. в scripts/install.sh

2. Библиотеки и миграции:
```shell
make
```

3. Запустить селери:
```shell
./manage.py celery worker --loglevel=DEBUG -c 5
```

4. Запустить торнадо:
```shell
./manage.py tornado-start
```

5. Запустить сервер:
```shell
./manage.py runserver
```

## Или

```shell
cd django-tornado-celery-example
vagrant up
```shell
