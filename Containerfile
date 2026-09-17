# syntax=docker/dockerfile:1
#
# mdjango's self-hosted docs site (site/) as a dynamic Django container — deploy shape (A).
# Built by .github/workflows/image.yml on push to main, pushed to a private ghcr.io package, and
# deployed by walden. The build context is the mdjango repo itself: it holds the package source,
# the committed theme assets, and site/ (config + docs content), so nothing is pulled cross-repo.
#
# Static is served by WhiteNoise from inside gunicorn (settings.py wires it at DEBUG=false):
# Django won't serve static at DEBUG=false, and walden's per-host Caddy is a plain reverse proxy.
#
# Intended eventual replacement: shape (B1) — a static export via `mdjango_build` served by a
# minimal static server, dogfooding mdjango's own export. Not yet.

# --- build stage: build the mdjango wheel (hatch-vcs derives the version from git, needs .git) ---
# git is required at build time: hatch-vcs/setuptools-scm shells out to it, and python:*-slim has
# no git binary. It lives only in this discarded builder stage, so the runtime image stays lean.
FROM python:3.14-slim AS builder
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY . .
RUN git config --global --add safe.directory /src \
    && pip install --no-cache-dir build \
    && python -m build --wheel --outdir /wheels

# --- runtime stage ------------------------------------------------------------------------------
FROM python:3.14-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/site \
    DJANGO_SETTINGS_MODULE=config.settings \
    DJANGO_DEBUG=false \
    WEB_CONCURRENCY=2

WORKDIR /app

# The mdjango wheel (deps resolved from PyPI) plus the site's runtime-only servers. gunicorn and
# whitenoise are the site's concern, not the package's, so they are not in mdjango's dependencies.
COPY --from=builder /wheels/*.whl /tmp/wheels/
RUN pip install --no-cache-dir /tmp/wheels/*.whl gunicorn whitenoise \
    && rm -rf /tmp/wheels

# site/ (the project package `config` + the docs content tree) is not part of the wheel.
COPY site/ /app/site/

# Gather mdjango's shipped static into STATIC_ROOT so WhiteNoise can serve it. DEBUG=false here,
# so this uses WhiteNoise's compressed-manifest storage; a broken static reference fails the build.
RUN python -m django collectstatic --noinput

EXPOSE 8000
# Worker count is a deploy-time concern (each worker holds its own in-memory registry, ADR 0001) —
# gunicorn reads WEB_CONCURRENCY natively, so walden sets it per host without an image rebuild;
# WEB_CONCURRENCY=2 above is the default. --threads adds in-worker I/O concurrency for static.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--threads", "4", "--access-logfile", "-"]
