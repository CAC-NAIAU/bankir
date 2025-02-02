from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .scheduler.scheduler import start

@receiver(post_migrate)
def start_scheduler(sender, **kwargs):
    start()
