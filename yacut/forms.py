import string
from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, SubmitField, URLField
from wtforms.validators import URL, DataRequired, Length, Optional, Regexp

ORIGINAL_LINK_LABEL = 'Оригинальная ссылка'
REQUIRED_MSG = 'Это поле обязательно'
INVALID_URL_MSG = 'Неверный формат ссылки'
SHORT = 'Твой вариант короткой ссылки'
TOO_LONG_MSG = 'Слишком длинное имя'
INVALID_CHARS_MSG = 'Допустимы только латинские буквы и цифры'
SUBMIT_LABEL = 'Создать'
FILES_LABEL = 'Выберите файлы'
FILES_REQUIRED_MSG = 'Выберите хотя бы один файл'
UPLOAD_LABEL = 'Загрузить'

MAX_URL_LENGTH = 2048
SHORT_LINK = 16
ALLOWED_CHARS = string.ascii_letters + string.digits
SHORT_LINK_PATTERN = rf'^[{ALLOWED_CHARS}]+$'


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
        SHORT,
        validators=[
            Length(max=SHORT_LINK, message=TOO_LONG_MSG),
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