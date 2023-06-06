from django.db import models
from django.db.models import Count
from django.utils.timezone import localtime


class EmailTracerManager(models.Manager):
    def insert(self, email: str):
        if email == '':
            pass
        else:
            self.create(receiver_email=email)

    def get_total_opened(self):
        data = []
        emails = self.values('receiver_email').annotate(count=Count('receiver_email'))
        for item in emails:
            _time = self.filter(receiver_email=item['receiver_email']).values_list('created_at', flat=True).last()
            data.append(
                {
                    'email': item['receiver_email'],
                    'count': item['count'],
                    'last_opened': localtime(_time).strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        return data
