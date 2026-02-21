import random
import string


def get_unique_short_id():
    """Только генерирует случайную строку из 6 символов."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))
