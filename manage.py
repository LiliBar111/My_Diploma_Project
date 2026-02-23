import os
import sys


def main():
    """Запуск административных задач Django."""
    # Указываю какой файл настроек использовать
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orders.settings')
    try:
        # Импортирую функцию выполнения команд
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Если Django не установлен - показываю понятную ошибку
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    # Выполняю команду из командной строки
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()