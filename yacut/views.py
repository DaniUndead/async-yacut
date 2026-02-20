import asyncio
import io
import os

import aiohttp
from dotenv import load_dotenv
from flask import (abort, current_app, flash, redirect, render_template,
                   send_file, url_for)

from . import app, db
from .forms import UploadForm, URLForm
from .models import URLMap
from .utils import get_unique_short_id

load_dotenv()
DISK_TOKEN = os.environ.get('DISK_TOKEN')


async def upload_file_to_yandex(session, file_obj, token):
    headers = {'Authorization': f'OAuth {DISK_TOKEN}'}
    base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
    filename = file_obj.filename
    disk_path = f'/{filename}'

    async with session.get(
        f'{base_url}/upload',
        params={'path': disk_path, 'overwrite': 'true'},
        headers=headers
    ) as resp:
        if resp.status != 200:
            data = await resp.json()
            raise Exception(f"Yandex Upload Error: {data.get('message')}")
        upload_url = (await resp.json())['href']

    file_data = file_obj.read()
    async with session.put(upload_url, data=file_data) as resp:
        resp.raise_for_status()

    async with session.get(
        f'{base_url}/download',
        params={'path': disk_path},
        headers=headers
    ) as resp:
        if resp.status != 200:
            data = await resp.json()
            raise Exception(f"Yandex Download Error: {data.get('message')}")

        await resp.json()

    return filename


async def get_fresh_download_link(filename):
    token = current_app.config.get('DISK_TOKEN')
    headers = {'Authorization': f'OAuth {token}'}
    base_url = 'https://cloud-api.yandex.net/v1/disk/resources/download'

    async with aiohttp.ClientSession() as session:
        async with session.get(
            base_url,
            params={'path': f'/{filename}'},
            headers=headers
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get('href')
    return None


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLForm()
    if form.validate_on_submit():
        original = form.original_link.data
        custom_id = form.custom_id.data

        if not custom_id:
            custom_id = get_unique_short_id()
        else:
            if (
                custom_id == 'files' or
                URLMap.query.filter_by(short=custom_id).first()
            ):
                flash(
                    'Предложенный вариант короткой ссылки уже существует.',
                    'error'
                )
                return render_template('index.html', form=form)

        new_link = URLMap(original=original, short=custom_id)
        db.session.add(new_link)
        db.session.commit()

        short_url = url_for(
            'redirect_view', short_id=custom_id, _external=True
        )
        return render_template('index.html', form=form, short_url=short_url)

    return render_template('index.html', form=form)


@app.route('/<string:short_id>')
async def redirect_view(short_id):
    link = URLMap.query.filter_by(short=short_id).first_or_404()

    if link.original.startswith("disk://"):
        filename = link.original.replace("disk://", "")
        fresh_url = await get_fresh_download_link(filename)

        if fresh_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(fresh_url) as resp:
                    if resp.status == 200:
                        file_bytes = await resp.read()
                        return send_file(
                            io.BytesIO(file_bytes),
                            download_name=filename,
                            as_attachment=True
                        )
            abort(404)

    return redirect(link.original)


@app.route('/files', methods=['GET', 'POST'])
def upload_view():
    form = UploadForm()

    if form.validate_on_submit():
        files = form.files.data
        token = app.config.get('DISK_TOKEN')

        async def upload_all(files_to_upload):
            async with aiohttp.ClientSession() as session:
                tasks = [
                    upload_file_to_yandex(session, f, token)
                    for f in files_to_upload
                ]
                return await asyncio.gather(*tasks)

        try:
            uploaded_filenames = asyncio.run(upload_all(files))

            for filename in uploaded_filenames:
                custom_id = get_unique_short_id()
                while URLMap.query.filter_by(short=custom_id).first():
                    custom_id = get_unique_short_id()

                new_link = URLMap(
                    original=f"disk://{filename}",
                    short=custom_id
                )
                db.session.add(new_link)

            db.session.commit()

        except Exception as e:
            flash(f'Ошибка: {e}', 'error')

    all_files = URLMap.query.filter(
        URLMap.original.startswith("disk://")
    ).order_by(URLMap.timestamp.desc()).all()
    saved_links = []

    for link in all_files:
        filename = link.original.replace("disk://", "")
        short_url = url_for(
            'redirect_view', short_id=link.short, _external=True
        )
        saved_links.append((filename, short_url))

    return render_template(
        'upload.html', form=form, saved_links=saved_links
    )