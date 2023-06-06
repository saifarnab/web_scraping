from django.contrib import admin
from .models import EmailTracer


@admin.register(EmailTracer)
class EmailTracerAdmin(admin.ModelAdmin):

    list_display = ['receiver_email', 'created_at']
    list_filter = ['receiver_email']
    search_fields = ['receiver_email']
