from django.contrib import admin

# Register your models here.
from clients.models import Clients


@admin.register(Clients)
class ClientsAdmin(admin.ModelAdmin):
    list_display = ('id', 'nodeid', 'addr', 'from_field', 'model', 'rssi', 'ssid', 'action', 'timestamp', 'time')
    actions = None
