import asyncio
from flask import flash, redirect, render_template

from . import app
from .constants import REDIRECT_ENDPOINT
from .forms import UploadForm, URLForm
from .models import URLMap
from .services import upload_files_to_yandex, YandexAPIError
from .utils import get_unique_short_id


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLForm()

    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    original = form.original_link.data
    short = form.custom_id.data or get_unique_short_id()

    if short == 'files' or URLMap.query.filter_by(short=short).first():
        flash('Предложенный вариант короткой ссылки уже существует.', 'error')
        return render_template('index.html', form=form)

    new_link = URLMap.create_short_link(original, short)

    return render_template(
        'index.html',
        form=form,
        short_url=new_link.get_short_link()
    )


@app.route('/<string:short>', endpoint=REDIRECT_ENDPOINT)
def redirect_view(short):
    """Перенаправление по короткой ссылке."""

    link = URLMap.get_by_short_or_404(short)

    return redirect(link.original)


@app.route('/files', methods=['GET', 'POST'])
def upload_view():
    form = UploadForm()

    if form.validate_on_submit():
        try:
            public_urls = asyncio.run(upload_files_to_yandex(form.files.data))

            for url in public_urls:
                short = get_unique_short_id()
                while URLMap.query.filter_by(short=short).first():
                    short = get_unique_short_id()

                URLMap.create_short_link(original=url, short=short)

            flash('Файлы успешно загружены', 'success')
            return redirect(app.url_for('upload_view'))

        except YandexAPIError as e:
            flash(f'Ошибка: {e}', 'error')

    all_files = URLMap.query.order_by(URLMap.timestamp.desc()).all()

    saved_links = [(
        link.original,
        link.get_short_link()
    ) for link in all_files]

    return render_template('upload.html', form=form, saved_links=saved_links)