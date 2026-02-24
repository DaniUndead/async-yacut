from flask import flash, redirect, render_template

from . import app
from .forms import UploadForm, URLForm
from .models import URLMap
from .services import YandexUploadError, upload_files_to_yandex

REDIRECT_VIEW_NAME = 'redirect_view'
EXISTING_ID_MSG = 'Предложенный вариант короткой ссылки уже существует.'


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLForm()

    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    try:
        return render_template(
            'index.html',
            form=form,
            short_url=URLMap.create_short_link(
                original=form.original_link.data,
                short=form.custom_id.data
            ).get_short_link()
        )
    except ValueError as error:

        flash(str(error), 'error')
        return render_template('index.html', form=form)


@app.route('/<string:short>', endpoint=REDIRECT_VIEW_NAME)
def redirect_view(short):
    """Редирект: если ссылка начинается на http — переход, иначе — 404."""
    url_record = URLMap.get_or_404(short)
    return redirect(url_record.original)


@app.route('/files', methods=['GET', 'POST'])
def upload_view():
    form = UploadForm()

    if not form.validate_on_submit():
        return render_template('upload.html', form=form)

    try:
        yandex_urls = upload_files_to_yandex(form.files.data)
    except YandexUploadError as error:
        flash(f'Ошибка загрузки на Яндекс.Диск: {error}', 'error')
        return render_template('upload.html', form=form)

    try:

        return render_template(
            'upload.html',
            form=form,
            saved_links=[
                (
                    filename,
                    URLMap.create_short_link(
                        original=url,
                        validate=False
                    ).get_short_link()
                )
                for filename, url in yandex_urls
            ]
        )
    except ValueError as error:
        flash(f'Ошибка базы данных: {error}', 'error')
        return render_template('upload.html', form=form)
