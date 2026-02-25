from flask import flash, redirect, render_template

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

    try:
        yandex_urls = upload_files_to_yandex(form.files.data)
    except Exception as error:
        flash(YANDEX_ERROR_MESSAGE.format(error=error), 'error')
        return render_template('upload.html', form=form)

    try:
        saved_links = []
        total_urls = len(yandex_urls)

        for index, url in enumerate(yandex_urls):
            is_last_item = (index == total_urls - 1)

            short_link_obj = URLMap.create(
                original=url,
                commit=is_last_item
            )
            saved_links.append(short_link_obj.get_short_link())

        return render_template(
            'upload.html',
            form=form,
            saved_links=saved_links
        )
    except ValueError as error:
        flash(LINK_ERROR_MESSAGE.format(error=error), 'error')
        return render_template('upload.html', form=form)
