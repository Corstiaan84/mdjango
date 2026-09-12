"""mdjango's self-hosted docs site — the ``site/`` project (ADR 0006).

mdjango's own public documentation site: it mounts mdjango at ``/docs`` and points it at the
documentation tree under ``content/``. Because it is a plain, default mount — no theme-seed
overrides, no shadowed shell — it doubles as the **canonical example** of consuming mdjango:
install ``django_cotton`` and ``mdjango``, point ``MDJANGO_CONTENT_DIR`` at a markdown tree, set
the shell branding, include the URLs. It is also the dev harness and pytest target. Nothing here
is shipped in the wheel.
"""

from pathlib import Path

import mdjango

BASE_DIR = Path(__file__).resolve().parent.parent

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

USE_TZ = True

# --- mdjango -----------------------------------------------------------------------------------
MDJANGO_CONTENT_DIR = BASE_DIR / "content"
MDJANGO_BRAND = "mdjango"
MDJANGO_HOME_URL = "/"
# The version chip is a display string; here it tracks the package, which a consumer's would not.
MDJANGO_VERSION = f"v{mdjango.__version__}"
# TODO: placeholder until the public repository exists.
MDJANGO_GITHUB_URL = "https://github.com/example/mdjango"
MDJANGO_SITE_TITLE = "mdjango docs"
# The one-line summary that heads the LLM artifacts (llms.txt / llms-full.txt).
MDJANGO_DESCRIPTION = (
    "A drop-in Django app that renders a tree of markdown into a documentation site."
)
# Response caching (ADR 0002): seconds for the server-side page cache + Cache-Control max-age.
# Off here because DEBUG=True (always_rebuild); shown for consumers who run with DEBUG=False.
MDJANGO_CACHE_SECONDS = 300
