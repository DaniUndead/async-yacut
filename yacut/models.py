from datetime import datetime
import random
import re
import string

from flask import url_for

from yacut import db

ALLOWED_CHARS = string.ascii_letters + string.digits
SHORT_ID_LENGTH = 6
MAX_URL_LENGTH = 2048
SHORT_LINK = 16
REDIRECT_VIEW_NAME = 'redirect_view'
SHORT_LINK_PATTERN = rf'^[{ALLOWED_CHARS}]+$'

ERROR_INVALID_NAME = 'Указано недопустимое имя для короткой ссылки'
ERROR_ALREADY_EXISTS = 'Предложенный вариант короткой ссылки уже существует.'
ERROR_URL_TOO_LONG = 'Указанная ссылка превышает допустимый размер.'
ERROR_RESERVED_NAME = (
    'Это имя зарезервировано системой '
    'и не может быть использовано.'
)

RESERVED_NAMES = ('api',)


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_URL_LENGTH), nullable=False)
    short = db.Column(
        db.String(SHORT_LINK),
        unique=True, nullable=False
    )
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def get_short_link(self):
        return url_for(REDIRECT_VIEW_NAME, short=self.short, _external=True)

    @staticmethod
    def get(short):
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def get_or_404(short):
        return URLMap.query.filter_by(short=short).first_or_404()

    @staticmethod
    def get_unique_short_id():
        """Генерирует уникальную строку, проверяя ее отсутствие в БД."""
        while True:
            short_id = ''.join(random.choices(
                ALLOWED_CHARS,
                k=SHORT_ID_LENGTH)
            )
            if not URLMap.get(short_id):
                return short_id

    @staticmethod
    def create_short_link(original, short=None, validate=True, commit=True):
        if not short:
            short = URLMap.get_unique_short_id()
        elif validate:
            if len(short) > SHORT_LINK or not re.match(
                SHORT_LINK_PATTERN,
                short
            ):
                raise ValueError(ERROR_INVALID_NAME)
            if short in RESERVED_NAMES:
                raise ValueError(ERROR_RESERVED_NAME)
            if URLMap.get(short) or short == 'files':
                raise ValueError(ERROR_ALREADY_EXISTS)

        if validate and len(original) > MAX_URL_LENGTH:
            raise ValueError(ERROR_URL_TOO_LONG)

        new_link = URLMap(original=original, short=short)
        db.session.add(new_link)

        if commit:
            db.session.commit()

        return new_link
