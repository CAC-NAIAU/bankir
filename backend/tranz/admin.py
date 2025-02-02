from django.contrib import admin

from .models import (
    Figurant, Transaction
)

admin.site.register(Figurant)
admin.site.register(Transaction)
