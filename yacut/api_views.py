from http import HTTPStatus

from flask import jsonify, request

from . import app
from .error_handlers import InvalidAPIUsage
from .models import URLMap

ERROR_NOT_FOUND = 'Указанный id не найден'
ERROR_NO_BODY = 'Отсутствует тело запроса'
ERROR_NO_URL_FIELD = '"url" является обязательным полем!'


@app.route('/api/id/<string:short>/', methods=['GET'])
def get_url(short):
    """API: Получение оригинальной ссылки по короткому ID"""
    record = URLMap.get(short)

    if not record:
        raise InvalidAPIUsage(ERROR_NOT_FOUND, HTTPStatus.NOT_FOUND)

    return jsonify({'url': record.original}), HTTPStatus.OK


@app.route('/api/id/', methods=['POST'])
def create_url():
    """API: Создание новой короткой ссылки"""
    data = request.get_json(silent=True)

    if data is None:
        raise InvalidAPIUsage(ERROR_NO_BODY)

    if 'url' not in data:
        raise InvalidAPIUsage(ERROR_NO_URL_FIELD)

    try:
        return jsonify({
            'url': data['url'],
            'short_link': URLMap.create(
                original=data['url'],
                short=data.get('custom_id')
            ).get_short_link()
        }), HTTPStatus.CREATED
    except ValueError as error:
        raise InvalidAPIUsage(str(error))
