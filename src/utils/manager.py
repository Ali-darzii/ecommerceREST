from django.db.models import Manager


class IsActiveSet(Manager):
    def get_query_set(self):
        return super(IsActiveSet, self).get_query_set().filter(is_active=True)
