---
title: Install and mount
weight: 10
description: Install mdjango into a Django project, write two markdown files, and open the rendered site.
---

# Install and mount

This tutorial takes an existing Django project from nothing to a rendered documentation page served
by your own `runserver`. It follows one path and skips every option. The how-to pages cover those.

**You need:** a Django 5.2+ project on Python 3.11+ with the default `startproject` settings:
`django.contrib.staticfiles` in `INSTALLED_APPS` and `APP_DIRS: True` in `TEMPLATES`. mdjango adds
no database tables, so there are no migrations to run.

## 1. Install the package

```bash
pip install django-mdjango
```

> mdjango is pre-release. Until the first release is published this command installs nothing from
> PyPI. Install from a checkout with `pip install -e .` instead.

The package depends on Django, `Markdown`, `pymdown-extensions`, `Pygments` and `django-cotton`.

## 2. Register the apps

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "django.contrib.staticfiles",
    "django_cotton",
    "mdjango",
]
```

Both apps are required. mdjango's templates are cotton components, and listing `django_cotton`
installs the template loader that compiles them.

## 3. Point mdjango at a content directory

```python
# settings.py
MDJANGO_CONTENT_DIR = BASE_DIR / "content"
MDJANGO_BRAND = "acme"
```

`MDJANGO_CONTENT_DIR` is the only required setting. `MDJANGO_BRAND` is the wordmark in the header.
Without it the site calls itself "docs".

## 4. Include the URLs

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    # ...
    path("docs/", include("mdjango.urls")),
]
```

To serve the docs at the site root instead (when the whole site is documentation), mount at `""` —
see [Serve the docs at the site root](../../reference/urls/#serve-the-docs-at-the-site-root).

## 5. Write two pages

```bash
mkdir -p content/guides
```

````markdown
<!-- content/_index.md -->
---
title: Acme docs
---

# Acme docs

Welcome. Start with the [first guide](guides/first-guide/).
````

````markdown
<!-- content/guides/first-guide.md -->
---
title: First guide
---

# First guide

## Install

Run the installer.

```bash
acme install
```

## Verify

Run `acme --version`.
````

## 6. Run the server and open the site

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/docs/>. You see your Index page with **acme** as the wordmark, a left
navigation holding a pinned *Acme docs* link and a *Guides* section, and the link to your first
guide. Click it. The page renders with an "On this page" table of contents built from the two `##`
headings, a copy button on the code block, and prev/next links at the bottom. Press `/` to open
search and type `installer`. The guide is found by its body text.

Edit `first-guide.md` and reload. With `DEBUG = True` the content is re-read on every request, so
the change is already there.

## Where next

- [Structure a content tree](../../how-to/structure-a-content-tree/) to add Sections, order them and
  group Pages.
- [Brand the header](../../how-to/brand-the-header/) to add a version chip, a GitHub link and a
  proper `<title>`.
- [Run in production](../../how-to/run-in-production/) before you deploy. `DEBUG = False` changes
  how content is read and cached.
