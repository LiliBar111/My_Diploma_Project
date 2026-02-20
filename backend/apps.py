from django.apps import AppConfig


class BackendConfig(AppConfig):
    """Конфигурация приложения backend"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'  # Имя приложения

    def ready(self):
        """При готовности приложения импортирую сигналы"""
        import backend.signals