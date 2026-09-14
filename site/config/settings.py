"""mdjango's self-hosted docs site — the ``site/`` project (ADR 0006).

mdjango's own public documentation site: it mounts mdjango at ``/docs`` and points it at the
documentation tree under ``content/``. Because it is a plain, default mount — no theme-seed
overrides, no shadowed shell — it doubles as the **canonical example** of consuming mdjango:
install ``django_cotton`` and ``mdjango``, point ``MDJANGO_CONTENT_DIR`` at a markdown tree, set
the shell branding, include the URLs. It is also the dev harness and pytest target. Nothing here
is shipped in the wheel.
"""

import os
from pathlib import Path

import mdjango

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(name, default):
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


# Env-driven for the container; dev-friendly defaults for the runserver harness.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-not-secret")
DEBUG = _env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",  # ships the sitemap.xml template the DocsSitemap view renders
    "django_cotton",  # auto-wires the cotton template loader
    "mdjango",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

# In production (the container) WhiteNoise serves the collected static from within gunicorn:
# Django won't serve static at DEBUG=False, and walden's per-host Caddy is a plain reverse proxy
# that doesn't serve an app's assets. Gated on DEBUG so the dev harness and tests need no
# WhiteNoise install (the middleware/storage are only referenced when DEBUG is False).
if not DEBUG:
    MIDDLEWARE.insert(0, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,  # cotton pops this and installs its own loader chain
        "OPTIONS": {"context_processors": []},
    },
]

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

if not DEBUG:
    # WhiteNoise compressed-manifest storage: hashed filenames + gzip/brotli + far-future caching.
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }

USE_TZ = True

# --- mdjango -----------------------------------------------------------------------------------
MDJANGO_CONTENT_DIR = BASE_DIR / "content"
MDJANGO_BRAND = "mdjango"
MDJANGO_HOME_URL = "/"
# The version chip is a display string; here it tracks the package, which a consumer's would not.
MDJANGO_VERSION = f"v{mdjango.__version__}"
MDJANGO_GITHUB_URL = "https://github.com/Corstiaan84/mdjango"
MDJANGO_SITE_TITLE = "mdjango docs"
# The one-line summary that heads the LLM artifacts (llms.txt / llms-full.txt).
MDJANGO_DESCRIPTION = (
    "A drop-in Django app that renders a tree of markdown into a documentation site."
)
# Response caching (ADR 0002): seconds for the server-side page cache + Cache-Control max-age.
# Off here because DEBUG=True (always_rebuild); shown for consumers who run with DEBUG=False.
MDJANGO_CACHE_SECONDS = 300
