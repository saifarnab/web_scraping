from django.db import models
from django.utils import timezone

from .managers import EmailTracerManager


class EmailTracer(models.Model):
    receiver_email = models.CharField(max_length=50, null=False, blank=False)
    created_at = models.DateTimeField(default=timezone.now)

    objects = EmailTracerManager()

    class Meta:
        verbose_name = 'Email Tracer'
        verbose_name_plural = 'Email Tracers'

    def __str__(self):
        return self.receiver_email
