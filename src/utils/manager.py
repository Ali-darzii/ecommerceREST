from django.utils import timezone
from django.db import models


class IsActiveSet(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class NowUntilEndSet(models.Manager):
    def get_queryset(self):
        now = timezone.now()
        return super().get_queryset().filter(is_active=True, start_date__lte=now, end_date__gt=now)