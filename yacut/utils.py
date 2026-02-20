import random
import string

from .models import URLMap


def get_unique_short_id(length=6):
    """Генерирует случайную строку из 6 символов и проверяет уникальность."""
    characters = string.ascii_letters + string.digits
    while True:
        short_id = ''.join(random.choices(characters, k=length))
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id
