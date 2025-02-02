from django.apps import AppConfig
# from .scheduler.scheduler import start
from django.db.models.signals import post_migrate

class TargetsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tranz'
    
    def ready(self):
        # start()
        import tranz.signals
