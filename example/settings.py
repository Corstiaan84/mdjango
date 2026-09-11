"""Example consumer project — the dev harness and pytest target for mdjango.

This is exactly what a consuming project's settings look like: install ``django_cotton`` and
``mdjango``, point ``MDJANGO_CONTENT_DIR`` at a markdown tree, set the shell branding, include the
URLs. Nothing here is shipped in the wheel.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = "dev-only-not-secret"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django_cotton",  # auto-wires the cotton template loader
    "mdjango",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "example.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,  # cotton pops this and installs its own loader chain
        "OPTIONS": {"context_processors": []},
    },
]

STATIC_URL = "/static/"

USE_TZ = True

# --- mdjango -----------------------------------------------------------------------------------
MDJANGO_CONTENT_DIR = BASE_DIR / "content"
MDJANGO_BRAND = "walden"
MDJANGO_HOME_URL = "/"
MDJANGO_VERSION = "v0.4.2"
MDJANGO_GITHUB_URL = "https://github.com/example/walden"
MDJANGO_SITE_TITLE = "walden docs"
# The one-line summary that heads the LLM artifacts (llms.txt / llms-full.txt).
MDJANGO_DESCRIPTION = "Deploy container apps to a server you own, with one config file."
# Response caching (ADR 0002): seconds for the server-side page cache + Cache-Control max-age.
# Off here because DEBUG=True (always_rebuild); shown for consumers who run with DEBUG=False.
MDJANGO_CACHE_SECONDS = 300
