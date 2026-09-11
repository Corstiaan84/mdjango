from django.apps import AppConfig


class MdjangoConfig(AppConfig):
    name = "mdjango"
    verbose_name = "mdjango documentation"
    # The registry is built lazily on first request (see features.content.services.get_registry),
    # not at import time, so management commands and system checks don't require content present.
