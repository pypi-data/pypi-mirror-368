# Django Admin Models Search

A Django package that adds a global search bar to the Django admin interface, allowing you to quickly search and navigate between registered models.

## Features

- Adds a global search bar to the Django admin header.
- Provides suggestions for registered models as you type.
- Supports keyboard navigation for quick access.
- Fully customizable and easy to integrate.

## Installation

Install the package via `pip`:

```bash
pip install django-admin-models-search
```

## Configuration 
1. Add the app to your INSTALLED_APPS in settings.py

```python
INSTALLED_APPS = [
    # Other apps...
    'django_admin_models_search',
]
```

2. Include the package's URLs in your urls.py

```python 
from django.urls import path, include

urlpatterns = [
    path('', include('django_admin_models_search.urls')),
]
```