Проект YaCut
Сервис для создания коротких ссылок с возможностью загрузки файлов на Яндекс.Диск.

Технологический стек:
Язык: Python 3.12

Фреймворк: Flask

База данных: SQLite (через SQLAlchemy)

Валидация: WTForms

Асинхронность: aiohttp, asyncio (для работы с Яндекс.Диском)

Фронтенд: Jinja2, Bootstrap

Как запустить проект:
Клонировать репозиторий и перейти в него:

Bash

git clone https://github.com/твой_логин/async-yacut.git
cd async-yacut
Создать и активировать виртуальное окружение:

Linux/macOS:

Bash

python3 -m venv venv
source venv/bin/activate
Windows:

Bash

python -m venv venv
source venv/Scripts/activate
Установить зависимости:

Bash

python -m pip install --upgrade pip
pip install -r requirements.txt
Настроить переменные окружения:
Создайте файл .env в корневой папке и добавьте настройки:

Фрагмент кода

FLASK_APP=yacut
FLASK_ENV=development
SECRET_KEY=секретный_ключ_для_форм
DATABASE_URL=sqlite:///db.sqlite3
DISK_TOKEN=твой_оаuth_токен_яндекс_диска
Инициализировать базу данных:

Bash

flask db upgrade
Запустить сервер:

Bash

flask run

Автор: Данис Хуснутдинов

GitHub: DaniUndead