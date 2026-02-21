import asyncio
import aiohttp
from flask import current_app


from .constants import YANDEX_API_BASE_URL


class YandexUploadError(RuntimeError):
    pass


async def _upload_single_file(session, file_obj, token):
    headers = {'Authorization': f'OAuth {token}'}
    filename = file_obj.filename
    disk_path = f'/{filename}'

    async with session.get(
        f'{YANDEX_API_BASE_URL}/upload',
        params={'path': disk_path, 'overwrite': 'true'},
        headers=headers
    ) as resp:
        resp.raise_for_status()
        upload_url = (await resp.json())['href']

    file_data = file_obj.read()
    async with session.put(upload_url, data=file_data) as resp:
        resp.raise_for_status()

    async with session.get(
        f'{YANDEX_API_BASE_URL}/download',
        params={'path': disk_path},
        headers=headers
    ) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return filename, data.get('href')


def upload_files_to_yandex(files):
    token = current_app.config.get('DISK_TOKEN')

    async def _upload_all():
        async with aiohttp.ClientSession() as session:
            tasks = [_upload_single_file(session, f, token) for f in files]
            return await asyncio.gather(*tasks)

    return asyncio.run(_upload_all())
