import re
from datetime import datetime
from flask import url_for
from yacut import db

from .constants import MAX_URL_LENGTH, SHORT_LINK_MAX_LEN, REDIRECT_ENDPOINT


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_URL_LENGTH), nullable=False)
    short = db.Column(
        db.String(SHORT_LINK_MAX_LEN),
        unique=True,
        nullable=False
    )
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def get_short_link(self):
        """Обычный метод: расчет абсолютного урла коротюльки"""
        return url_for(REDIRECT_ENDPOINT, short=self.short, _external=True)

    @staticmethod
    def get_by_short_or_404(cls, short):
        return cls.query.filter_by(short=short).first_or_404()

    @classmethod
    def create_short_link(cls, original, short=None):
        if not short:
            short = get_by_short_or_404_id()
            while cls.get_by_short(short):
                short = get_by_short_or_404_id()
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