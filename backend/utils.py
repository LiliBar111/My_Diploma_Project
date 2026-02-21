"""
Вспомогательные функции для приложения.
"""
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


def validate_url(url):
    """
    Проверяю корректность URL.
    """
    validator = URLValidator()
    try:
        validator(url)
        return True, None
    except ValidationError as e:
        return False, str(e)