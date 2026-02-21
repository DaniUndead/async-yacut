import re
from datetime import datetime
from flask import url_for

from yacut import db
from .utils import get_unique_short_id
from .constants import SHORT_LINK_MAX_LEN, MAX_URL_LENGTH, REDIRECT_VIEW_NAME
from yacut import db


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_URL_LENGTH), nullable=False)
    short = db.Column(
        db.String(SHORT_LINK_MAX_LEN),
        unique=True, nullable=False
    )
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def get_short_link(self):
        return url_for(REDIRECT_VIEW_NAME, short=self.short, _external=True)

    @classmethod
    def get_by_short(cls, short):
        return cls.query.filter_by(short=short).first()

    @classmethod
    def get_by_short_or_404(cls, short):
        return cls.query.filter_by(short=short).first_or_404()

    @classmethod
    def create_short_link(cls, original, short=None):
        if not short:
            short = get_unique_short_id()
            while cls.get_by_short(short):
                short = get_unique_short_id()
        else:
            if len(short) > 16 or not re.match(r'^[a-zA-Z0-9]+$', short):
                raise ValueError(
                    'Указано недопустимое имя для короткой ссылки'
                )
            if cls.get_by_short(short):
                raise ValueError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )

        new_link = cls(original=original, short=short)
        db.session.add(new_link)
        db.session.commit()
        return new_link

    @classmethod
    def get_uploaded_files(cls):
        return cls.query.filter(
            cls.original.like('%yandex%')
        ).order_by(cls.timestamp.desc()).all()