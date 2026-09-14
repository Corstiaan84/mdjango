"""WSGI entry point for the ``site/`` project — mdjango's self-hosted docs site.

Used by gunicorn in the container image (``gunicorn config.wsgi:application``). ``site/`` is on the
``PYTHONPATH`` so ``config`` resolves; ``manage.py`` handles the same wiring for local commands.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
