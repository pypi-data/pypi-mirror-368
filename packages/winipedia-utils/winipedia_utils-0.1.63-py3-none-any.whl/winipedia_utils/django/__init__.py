"""__init__ module for winipedia_utils.django."""

import django
import django_stubs_ext
from django.conf import settings

from winipedia_utils.logging.logger import get_logger

logger = get_logger(__name__)

django_stubs_ext.monkeypatch()
logger.info("Monkeypatched django-stubs")

if not settings.configured:
    logger.info("Configuring minimal django settings")
    settings.configure(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
    )
    django.setup()
