from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, Length, Optional, URL


class URLForm(FlaskForm):
    original_link = StringField(
        'Оригинальная ссылка',
        validators=[DataRequired(
            message="Это поле обязательно"),
            URL(message="Неверный формат ссылки")]
    )
    custom_id = StringField(
        'Твой вариант короткой ссылки',
        validators=[Length(max=16, message="Слишком длинное имя"), Optional()]
    )
    submit = SubmitField('Создать')


class UploadForm(FlaskForm):
    files = MultipleFileField(
        'Выберите файлы',
        validators=[DataRequired(message="Выберите хотя бы один файл")]
    )
    submit = SubmitField('Загрузить')
