from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, SubmitField, URLField
from wtforms.validators import URL, DataRequired, Length, Optional, Regexp

from .constants import MAX_URL_LENGTH, SHORT_LINK_MAX_LEN, SHORT_LINK_PATTERN

ORIGINAL_LINK_LABEL = 'Оригинальная ссылка'
REQUIRED_MSG = 'Это поле обязательно'
INVALID_URL_MSG = 'Неверный формат ссылки'
CUSTOM_ID_LABEL = 'Твой вариант короткой ссылки'
TOO_LONG_MSG = 'Слишком длинное имя'
INVALID_CHARS_MSG = 'Допустимы только латинские буквы и цифры'
SUBMIT_LABEL = 'Создать'
FILES_LABEL = 'Выберите файлы'
FILES_REQUIRED_MSG = 'Выберите хотя бы один файл'
UPLOAD_LABEL = 'Загрузить'


class URLForm(FlaskForm):
    original_link = URLField(
        ORIGINAL_LINK_LABEL,
        validators=[
            DataRequired(message=REQUIRED_MSG),
            Length(max=MAX_URL_LENGTH, message=TOO_LONG_MSG),
            URL(message=INVALID_URL_MSG)
        ]
    )
    custom_id = StringField(
        CUSTOM_ID_LABEL,
        validators=[
            Length(max=SHORT_LINK_MAX_LEN, message=TOO_LONG_MSG),
            Regexp(SHORT_LINK_PATTERN, message=INVALID_CHARS_MSG),
            Optional()
        ]
    )
    submit = SubmitField(SUBMIT_LABEL)


class UploadForm(FlaskForm):
    files = MultipleFileField(
        FILES_LABEL,
        validators=[DataRequired(message=FILES_REQUIRED_MSG)]
    )
    submit = SubmitField(UPLOAD_LABEL)