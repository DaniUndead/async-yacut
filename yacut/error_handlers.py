from flask import render_template, jsonify, request
from . import app


@app.errorhandler(404)
def page_not_found(error):

    if request.path.startswith('/api/'):
        return jsonify({'message': 'Ресурс не найден'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'message': 'Внутренняя ошибка сервера'}), 500
    return render_template('500.html'), 500
