from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, SubmitField, URLField
from wtforms.validators import URL, DataRequired, Length, Optional, Regexp

from .constants import MAX_URL_LENGTH, SHORT_MAX_LEN, SHORT_PATTERN

ORIGINAL_LINK_LABEL = 'Оригинальная ссылка'
REQUIRED_MESSAGE = 'Это поле обязательно'
INVALID_URL_MESSAGE = 'Неверный формат ссылки'
SHORT = 'Твой вариант короткой ссылки'
TOO_LONG_MESSAGE = 'Слишком длинное имя'
INVALID_CHARS_MESSAGE = 'Допустимы только латинские буквы и цифры'
SUBMIT_LABEL = 'Создать'
FILES_LABEL = 'Выберите файлы'
FILES_REQUIRED_MESSAGE = 'Выберите хотя бы один файл'
UPLOAD_LABEL = 'Загрузить'


class URLForm(FlaskForm):
    original_link = URLField(
        ORIGINAL_LINK_LABEL,
        validators=[
            DataRequired(message=REQUIRED_MESSAGE),
            Length(max=MAX_URL_LENGTH, message=TOO_LONG_MESSAGE),
            URL(message=INVALID_URL_MESSAGE)
        ]
    )
    custom_id = StringField(
        SHORT,
        validators=[
            Length(max=SHORT_MAX_LEN, message=TOO_LONG_MESSAGE),
            Regexp(SHORT_PATTERN, message=INVALID_CHARS_MESSAGE),
            Optional()
        ]
    )
    submit = SubmitField(SUBMIT_LABEL)


class UploadForm(FlaskForm):
    files = MultipleFileField(
        FILES_LABEL,
        validators=[DataRequired(message=FILES_REQUIRED_MESSAGE)]
    )
    submit = SubmitField(UPLOAD_LABEL)
