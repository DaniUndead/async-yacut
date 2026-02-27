from flask import flash, redirect, render_template, request

from . import app
from .constants import REDIRECT_VIEW_NAME
from .forms import UploadForm, URLForm
from .models import URLMap
from .services import upload_files_to_yandex

YANDEX_ERROR_MESSAGE = 'Ошибка загрузки на Яндекс.Диск: {error}'
LINK_ERROR_MESSAGE = 'Ошибка обработки ссылки: {error}'


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLForm()

    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    try:
        return render_template(
            'index.html',
            form=form,
            short_url=URLMap.create(
                original=form.original_link.data,
                short=form.custom_id.data,
                validate=False
            ).get_short_link()
        )
    except ValueError as error:

        flash(str(error), 'error')
        return render_template('index.html', form=form)


@app.route('/<string:short>', endpoint=REDIRECT_VIEW_NAME)
def redirect_view(short):
    """Редирект: если ссылка начинается на http — переход, иначе — 404."""
    return redirect(URLMap.get_or_404(short).original)


@app.route('/files', methods=['GET', 'POST'])
def upload_view():
    form = UploadForm()
    if not form.validate_on_submit():
        return render_template('upload.html', form=form)
    uploaded_files = form.files.data
    try:
        yandex_urls = upload_files_to_yandex(uploaded_files)
    except Exception as error:
        flash(YANDEX_ERROR_MESSAGE.format(error=error), 'error')
        return render_template('upload.html', form=form)
    try:
        return render_template(
            'upload.html',
            form=form,
            saved_links=[
                (file_obj.filename, URLMap.create(
                    original=url
                ).get_short_link())
                for file_obj, url in zip(uploaded_files, yandex_urls)
            ]
        )
    except ValueError as error:
        flash(LINK_ERROR_MESSAGE.format(error=error), 'error')
        return render_template('upload.html', form=form)
