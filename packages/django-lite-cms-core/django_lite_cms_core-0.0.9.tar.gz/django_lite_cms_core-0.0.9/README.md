# django-lite-cms-core

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Django CI run test](https://github.com/christianwgd/django-lite-cms-core/actions/workflows/django-test.yml/badge.svg)](https://github.com/christianwgd/django-lite-cms-core/actions/workflows/django-test.yml)
[![codecov](https://codecov.io/gh/christianwgd/django-lite-cms-core/graph/badge.svg?token=azVWLmIFmg)](https://codecov.io/gh/christianwgd/django-lite-cms-core)
[![PyPI](https://img.shields.io/pypi/v/django-lite-cms-core)](https://pypi.org/project/django-lite-cms-core/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/django-lite-cms-core)

``django-lite-cms``is a lightweight and modular CMS addon for Django inspired
by [Mezzanine](https://github.com/stephenmcd/mezzanine) CMS. This package contains the core classes that are needed 
to get basic CMS properties.

I've started with [Mezzanine](https://github.com/stephenmcd/mezzanine) CMS for my projects but soon found it a little 
bit too heavy for my purposes. Unfortunately Mezzanine was not optimal supported 
by the community (at this time it has open vulnerabilities and the latest Django version
supported is 4.0) so I needed a lighter approach that would also be a lot more modular. 
Since my code was only project local and I copied the code around between 
different projects, I started to put the code in installable libraries.

## Features

- Base classes with
  - Properties: title, publish_date, expiry_date
  - Status model (currently DRAFT and PUBLISHED) with scheduled publishing
  - Manager with "published" query, based on status and date fields
  - Supporting multilingual sites
  - Search functionality
  - Admin edit links in frontend
  - HTML content field with tinymce5


## Documentation

Documentation is available at https://django-lite-cms-core.readthedocs.io.

Please note that the docs are work in progress, so it is not completed by now and 
will be subject to change.

## Outlook

There will come some more add-ons for this lib:

- A hierarchical page model with menus
- A blog app
- ...
