from django.apps import AppConfig


class FollowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'follow'


    def ready(self):
        from . import signals