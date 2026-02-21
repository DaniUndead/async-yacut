from flask import jsonify, request
from http import HTTPStatus

from . import app
from .models import URLMap
from .error_handlers import InvalidAPIUsage


@app.route('/api/id/<string:short>/', methods=['GET'])
def get_url(short):
    """API: Получение оригинальной ссылки по короткому ID"""

    url_record = URLMap.get_by_short(short)

    if not url_record:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)

    return jsonify({'url': url_record.original}), HTTPStatus.OK


@app.route('/api/id/', methods=['POST'])
def create_url():
    """API: Создание новой короткой ссылки"""
    data = request.get_json(silent=True)

    if data is None:
        raise InvalidAPIUsage(
            'Отсутствует тело запроса',
            HTTPStatus.BAD_REQUEST
        )

    if 'url' not in data:
        raise InvalidAPIUsage(
            '"url" является обязательным полем!',
            HTTPStatus.BAD_REQUEST
        )

    try:
        new_record = URLMap.create_short_link(
            original=data['url'],
            short=data.get('custom_id')
        )
    except ValueError as error:
        raise InvalidAPIUsage(str(error), HTTPStatus.BAD_REQUEST)

    return jsonify({
        'url': data['url'],
        'short_link': new_record.get_short_link()
    }), HTTPStatus.CREATED
