import asyncio
import os

import aiohttp

YANDEX_API_BASE_URL = 'https://cloud-api.yandex.net/v1/disk/resources'

YANDEX_UPLOAD_URL = f'{YANDEX_API_BASE_URL}/upload'
YANDEX_DOWNLOAD_URL = f'{YANDEX_API_BASE_URL}/download'
YANDEX_TOKEN = os.getenv('DISK_TOKEN', 'твой_токен_по_умолчанию_если_нужно')
YANDEX_HEADERS = {'Authorization': f'OAuth {YANDEX_TOKEN}'}


class YandexUploadError(RuntimeError):
    pass


async def _upload_single_file(session, file_obj):
    async with session.get(
        YANDEX_UPLOAD_URL,
        params={'path': f'/{file_obj.filename}', 'overwrite': 'true'},
        headers=YANDEX_HEADERS
    ) as resp:
        resp.raise_for_status()
        upload_url = (await resp.json())['href']

    async with session.put(upload_url, data=file_obj.read()) as resp:
        resp.raise_for_status()

    async with session.get(
        YANDEX_DOWNLOAD_URL,
        params={'path': f'/{file_obj.filename}'},
        headers=YANDEX_HEADERS
    ) as resp:
        resp.raise_for_status()
        return (await resp.json()).get('href')


def upload_files_to_yandex(files):
    async def _upload_all():
        async with aiohttp.ClientSession() as session:
            return await asyncio.gather(
                *[_upload_single_file(session, f) for f in files]
            )
    return asyncio.run(_upload_all())
