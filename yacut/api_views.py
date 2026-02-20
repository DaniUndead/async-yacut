import re

from flask import jsonify, request

from . import app, db
from .models import URLMap
from .utils import get_unique_short_id


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_url(short_id):
    """API: Получение оригинальной ссылки по короткому ID"""
    link = URLMap.query.filter_by(short=short_id).first()
    if not link:
        return jsonify({'message': 'Указанный id не найден'}), 404

    return jsonify({'url': link.original}), 200

@app.route('/api/id/', methods=['POST'])
def create_url():
    """API: Создание новой короткой ссылки"""
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({'message': 'Отсутствует тело запроса'}), 400

    if 'url' not in data:
        return jsonify({'message': '"url" является обязательным полем!'}), 400

    original = data['url']
    custom_id = data.get('custom_id')

    if not custom_id:
        custom_id = get_unique_short_id()
    else:
        if len(custom_id) > 16 or not re.match(r'^[a-zA-Z0-9]+$', custom_id):
            return jsonify(
                {'message': 'Указано недопустимое имя для короткой ссылки'}
            ), 400

        if URLMap.query.filter_by(short=custom_id).first():
            return jsonify(
                {'message':
                 'Предложенный вариант короткой ссылки уже существует.'}
            ), 400

    new_link = URLMap(original=original, short=custom_id)
    db.session.add(new_link)
    db.session.commit()
    return jsonify({
        'url': new_link.original,
        'short_link': request.host_url + new_link.short
    }), 201
