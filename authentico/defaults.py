from django.conf import settings

AUTHENTICO_PASSWORD_MIN_LENGTH = getattr(settings, 'AUTHENTIC_PASSWORD_MIN_LENGTH', 6)
