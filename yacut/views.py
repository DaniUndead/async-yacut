from flask import flash, redirect, render_template, url_for

from . import app
from .forms import UploadForm, URLForm
from .models import URLMap
from .constants import REDIRECT_VIEW_NAME, EXISTING_ID_MSG
from .services import upload_files_to_yandex


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLForm()

    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    custom_id = form.custom_id.data


    if custom_id and (custom_id == 'files' or URLMap.get_by_short(custom_id)):
        flash(EXISTING_ID_MSG, 'error')

        form.custom_id.errors.append(EXISTING_ID_MSG)

        return render_template('index.html', form=form)

    new_link = URLMap.create_short_link(
        original=form.original_link.data,
        short=custom_id
    )

    return render_template(
        'index.html',
        form=form,
        short_url=new_link.get_short_link()
    )


@app.route('/<string:short>', endpoint=REDIRECT_VIEW_NAME)
def redirect_view(short):
    """Редирект: если ссылка начинается на http — переход, иначе — 404."""
    link = URLMap.get_by_short_or_404(short)
    return redirect(link.original)


@app.route('/files', methods=['GET', 'POST'])
def upload_view():
    form = UploadForm()
    saved_links = []

    if form.validate_on_submit():
        try:
            # Загружаем файлы и сразу создаем для них короткие ссылки
            results = upload_files_to_yandex(form.files.data)
            saved_links = [
                (filename, URLMap.create_short_link(original=url).get_short_link())
                for filename, url in results
            ]
        except Exception as e:
            flash(f'Ошибка: {e}', 'error')

    return render_template('upload.html', form=form, saved_links=saved_links)
