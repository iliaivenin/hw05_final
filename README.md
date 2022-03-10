# Yatube
Социальная сеть для публикации блогов.

Разработана по MVT архитектуре. Регистрация реализована с верификацией данных, сменой и восстановлением пароля через почту. Используется пагинация постов и кеширование. Написаны тесты, проверяющие работу сервиса.

## Стек технологий
Python, Django, SQLite3, unittest.

## Установка
Создайте виртуальное окружение:
```bash
python -m venv venv
```
Активируйте его:
```bash
source venv/Scripts/activate
```
Используйте [pip](https://pip.pypa.io/en/stable/), чтобы установить зависимости:
```bash
pip install -r requirements.txt
```
После примените все миграции:
```bash
python manage.py migrate
```
Соберите статику:
```bash
python manage.py collectstatic
```
И запускайте сервер:
```bash
python manage.py runserver
```

## Тесты
Чтобы запустить тесты, воспользуйтесь командой:
```bash
python manage.py test -v2
```
Тесты расположены в папке: ```./posts/tests/```
