import asyncio
import aiohttp
from flask import render_template, redirect, url_for, flash, abort, request
from . import app, db
from .models import URLMap
from .forms import URLForm, UploadForm
from .utils import get_unique_short_id


async def upload_file_to_yandex(session, file_obj, token):
    headers = {'Authorization': f'OAuth {token}'}
    base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
    filename = file_obj.filename

    disk_path = f'/{filename}'

    async with session.get(
        f'{base_url}/upload',
        params={'path': disk_path, 'overwrite': 'true'},
        headers=headers
    ) as resp:
        data = await resp.json()
        upload_url = data['href']

    file_data = file_obj.read()
    async with session.put(upload_url, data=file_data) as resp:
        resp.raise_for_status()

    async with session.get(
        f'{base_url}/download',
        params={'path': disk_path},
        headers=headers
    ) as resp:
        data = await resp.json()
        download_url = data['href']

    return filename, download_url


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
            'redirect_view',
            short_id=custom_id, _external=True
        )
        return render_template('index.html', form=form, short_url=short_url)

    return render_template('index.html', form=form)


@app.route('/<string:short_id>')
def redirect_view(short_id):
    link = URLMap.query.filter_by(short=short_id).first_or_404()
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

        results = asyncio.run(upload_all(files))

        saved_links = []
        for filename, download_url in results:

            custom_id = get_unique_short_id()
            while URLMap.query.filter_by(short=custom_id).first():
                custom_id = get_unique_short_id()

            new_link = URLMap(original=download_url, short=custom_id)
            db.session.add(new_link)
            db.session.commit()

            short_url = url_for(
                'redirect_view',
                short_id=custom_id, _external=True
            )
            saved_links.append((filename, short_url))

        return render_template(
            'upload.html',
            form=form, saved_links=saved_links
        )

    return render_template('upload.html', form=form)
