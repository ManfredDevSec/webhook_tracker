from django.contrib import admin
from .models import WebhookRequest

@admin.register(WebhookRequest)
class WebhookRequestAdmin(admin.ModelAdmin):
    list_display = ['tracking_id', 'ip_address', 'country', 'city', 'timestamp']
    list_filter = ['tracking_id', 'country', 'timestamp']
    search_fields = ['tracking_id', 'ip_address', 'user_agent']
    readonly_fields = ['timestamp']