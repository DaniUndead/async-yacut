from http import HTTPStatus

from flask import jsonify, render_template, request

from . import app, db


class InvalidAPIUsage(Exception):
    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message, status_code=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return dict(message=self.message)


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'message': 'Ресурс не найден'}), HTTPStatus.NOT_FOUND
    return render_template('404.html'), HTTPStatus.NOT_FOUND


@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_error(error):
    db.session.rollback()

    if request.path.startswith('/api/'):
        return jsonify(
            ({'message': 'Внутренняя ошибка сервера'}),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR
