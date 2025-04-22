from django.apps import AppConfig



class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'

    def ready(self):
        from . import signals as _signals  # noqa: F401 - import signals to connect them
