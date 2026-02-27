import random
import re
from datetime import datetime

from flask import url_for

from yacut import db

from .constants import (ALLOWED_CHARS, MAX_GENERATION_ATTEMPTS, MAX_URL_LENGTH,
                        REDIRECT_VIEW_NAME, RESERVED_SHORT_NAMES, SHORT_LENGTH,
                        SHORT_MAX_LEN, SHORT_PATTERN)

INVALID_SHORT_NAME_MESSAGE = 'Указано недопустимое имя для короткой ссылки'
SHORT_NAME_TAKEN_MESSAGE = (
    'Предложенный вариант короткой ссылки уже существует.'
)
URL_TOO_LONG_MESSAGE = (
    'Указанная ссылка превышает допустимый '
    f'размер в {MAX_URL_LENGTH} символов.'
)
GENERATION_FAILED_MESSAGE = 'Не удалось сгенерировать уникальную короткую ссылку'


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_URL_LENGTH), nullable=False)
    short = db.Column(
        db.String(SHORT_MAX_LEN),
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
    def get_unique_short():
        for _ in range(MAX_GENERATION_ATTEMPTS):
            short = ''.join(random.choices(
                ALLOWED_CHARS,
                k=SHORT_LENGTH
            ))
            if short not in RESERVED_SHORT_NAMES and not URLMap.get(short):
                return short
        raise RuntimeError(GENERATION_FAILED_MESSAGE)

    @staticmethod
    def create(original, short=None, validate=True, commit=True):
        if not short:
            short = URLMap.get_unique_short()
        else:
            if validate:
                if len(short) > SHORT_MAX_LEN or not re.match(
                    SHORT_PATTERN,
                    short
                ):
                    raise ValueError(INVALID_SHORT_NAME_MESSAGE)
            if URLMap.get(short) or short in RESERVED_SHORT_NAMES:
                raise ValueError(SHORT_NAME_TAKEN_MESSAGE)
        if validate and len(original) > MAX_URL_LENGTH:
            raise ValueError(URL_TOO_LONG_MESSAGE)
        url_record = URLMap(original=original, short=short)
        db.session.add(url_record)
        if commit:
            db.session.commit()
        return url_record
