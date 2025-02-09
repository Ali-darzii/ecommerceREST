from django.utils import timezone
from django.db.models import Manager

class IsActiveSet(Manager):
    def get_query_set(self):
        return super(IsActiveSet, self).get_query_set().filter(is_active=True)


class NowUntilEndSet(Manager):
    def get_query_set(self):
        now = timezone.now()
        return super(NowUntilEndSet, self).get_query_set().filter(is_active=True,start_date__lte=now, end_date__gt=now)