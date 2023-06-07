import datetime

from django.db import models
from django.db.models import Count
from django.utils import timezone


class EmailTracerManager(models.Manager):
    def insert(self, email: str):
        if email == '':
            pass
        else:
            last_entry = self.filter(receiver_email=email).last()
            if last_entry is not None:
                print(timezone.now() - last_entry.created_at)
                if (timezone.now() - last_entry.created_at) > datetime.timedelta(seconds=30):
                    self.create(receiver_email=email)
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
                    'last_opened': timezone.localtime(_time).strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        return data
