---
title: Install and mount
weight: 10
description: Install mdjango into a Django project, write two markdown files, and open the rendered site.
---

# Install and mount

This tutorial takes an existing Django project from nothing to a rendered documentation page. It
follows one path and skips every option; the how-to pages cover those.

**You need:** a Django 5.2+ project on Python 3.11+ with the default `startproject` settings —
`django.contrib.staticfiles` in `INSTALLED_APPS` and `APP_DIRS: True` in `TEMPLATES`. mdjango
adds no database tables, so no migrations are involved.

## 1. Install the package

<!-- TODO(docs): pre-PyPI — the install command below is the intended one and is a placeholder
until the first release is published. -->

```bash
pip install django-mdjango
```

This pulls in Django, `Markdown`, `pymdown-extensions`, `Pygments` and `django-cotton`.

## 2. Register the apps

Add both `django_cotton` and `mdjango` to `INSTALLED_APPS`. mdjango's templates are cotton
components; listing `django_cotton` wires up the template loader that compiles them.

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "django.contrib.staticfiles",
    "django_cotton",
    "mdjango",
]
```

## 3. Point mdjango at a content directory

`MDJANGO_CONTENT_DIR` is the only required setting. `MDJANGO_BRAND` is the wordmark in the header;
without it the site calls itself "docs".

```python
# settings.py
MDJANGO_CONTENT_DIR = BASE_DIR / "content"
MDJANGO_BRAND = "acme"
```

## 4. Include the URLs

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    # ...
    path("docs/", include("mdjango.urls")),
]
```

## 5. Write two pages

Create the directory and two files. The root `_index.md` is the landing page; the subdirectory is a
Section; the file inside it is a Page.

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

Open <http://127.0.0.1:8000/docs/>. You see the landing page with **acme** as the wordmark, a
left navigation holding a pinned *Acme docs* link and a *Guides* section, and the link to your
first guide. Click it: the page renders with an "On this page" table of contents built from the two
`##` headings, a copy button on the code block, and prev/next links at the bottom. Press `/` to open
search and type `installer` — the guide is found by its body text.

Edit `first-guide.md` and reload. With `DEBUG = True` the content is re-read on every request, so
the change is already there.

## Where next

- [Structure a content tree](../../how-to/structure-a-content-tree/) to add sections, order them
  and group pages.
- [Brand the header](../../how-to/brand-the-header/) to add a version, a GitHub link and a proper
  `<title>`.
- [Run in production](../../how-to/run-in-production/) before you deploy — `DEBUG = False` changes
  how content is read and cached.
