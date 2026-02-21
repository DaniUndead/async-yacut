import asyncio
import aiohttp
from http import HTTPStatus

from .constants import YANDEX_API_BASE_URL, YANDEX_HEADERS


class YandexAPIError(Exception):
    """Кастомное исключение для ошибок Яндекс.Диска"""
    pass

async def _upload_single_file(session, file_obj):
    filename = file_obj.filename
    disk_path = f'/{filename}'

    async with session.get(
        f'{YANDEX_API_BASE_URL}/upload',
        params={'path': disk_path, 'overwrite': 'true'},
        headers=YANDEX_HEADERS
    ) as resp:
        if resp.status != HTTPStatus.OK:
            raise YandexAPIError(
                f'Ошибка Яндекса при получении URL для {filename}'
            )
        upload_url = (await resp.json())['href']

    async with session.put(upload_url, data=file_obj.read()) as resp:
        resp.raise_for_status()

    async with session.put(
        f'{YANDEX_API_BASE_URL}/publish',
        params={'path': disk_path},
        headers=YANDEX_HEADERS
    ) as resp:
        resp.raise_for_status()

    async with session.get(
        YANDEX_API_BASE_URL,
        params={'path': disk_path},
        headers=YANDEX_HEADERS
    ) as resp:
        if resp.status != HTTPStatus.OK:
            raise YandexAPIError(
                'Ошибка Яндекса при получении публичной ссылки'
            )
        public_url = (await resp.json()).get('public_url')

    return public_url

async def upload_files_to_yandex(session, file_obj, token):
    headers = {'Authorization': f'OAuth {token}'}
    filename = file_obj.filename
    disk_path = f'/{filename}'

    # 1. Получение ссылки для загрузки
    async with session.get(
        f'{YANDEX_API_BASE_URL}/upload',
        params={'path': disk_path, 'overwrite': 'true'},
        headers=headers
    ) as resp:
        resp.raise_for_status()
        upload_url = (await resp.json())['href']

    # 2. Загрузка файла
    file_data = file_obj.read()
    async with session.put(upload_url, data=file_data) as resp:
        resp.raise_for_status()

    # 3. Получение ссылки для скачивания (как требуют тесты!)
    async with session.get(
        f'{YANDEX_API_BASE_URL}/download',
        params={'path': disk_path},
        headers=headers
    ) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return data.get('href')
