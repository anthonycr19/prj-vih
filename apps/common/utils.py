import pytz

from django.utils import timezone


def get_now(tz='America/Lima'):
    timezone.activate(pytz.timezone(tz))
    return timezone.localtime(timezone.now())
