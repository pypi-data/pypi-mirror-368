# django-gar
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/) 
[![Django 4.x](https://img.shields.io/badge/django-4.2-blue.svg)](https://docs.djangoproject.com/en/4.2/)
[![Python CI](https://github.com/briefmnews/django-gar/actions/workflows/workflow.yml/badge.svg)](https://github.com/briefmnews/django-gar/actions/workflows/workflow.yml)
[![codecov](https://codecov.io/gh/briefmnews/django-gar/branch/master/graph/badge.svg)](https://codecov.io/gh/briefmnews/django-gar)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)  

Django app to handle CAS authentication and resource management for the french Gestionnaire d'Accès aux Ressources (GAR).

## Features
- CAS authentication with GAR
- Institution management with subscription tracking
- Allocation monitoring for resources
- Caching of GAR data (allocations, subscriptions, ENT IDs)
- Admin interface for institution management
- CSV export of allocation reports

## Installation
Install with [pip](https://pip.pypa.io/en/stable/):
```shell
pip install django-gar
```

## Setup
In order to make `django-gar` work, you'll need to follow these steps:

### 1. Settings
Add the required configuration to your settings:
```python
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',

    'django_gar',
    ...
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    'django_gar.middleware.GARMiddleware', # mandatory
    ...
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    
    'django_gar.backends.GARBackend',
    ...
)
```

### 2. Migrations
Run migrations to create the necessary database tables:
```shell
python manage.py migrate
```

### 3. Required Settings
Configure these mandatory settings:
```python
# GAR Connection Settings
GAR_BASE_URL = "https://idp-auth.partenaire.test-gar.education.fr/"
GAR_BASE_SUBSCRIPTION_URL = "https://abonnement.partenaire.test-gar.education.fr/"
GAR_SUBSCRIPTION_PREFIX = "your_prefix"
GAR_DISTRIBUTOR_ID = "your_distributor_id"

# Authentication Certificates
GAR_CERTIFICATE_PATH = "/path/to/your/cert.pem"
GAR_KEY_PATH = "/path/to/your/key.pem"

# Resource Configuration
GAR_RESOURCES_ID = "your_resource_id"
GAR_ORGANIZATION_NAME = "Your Organization"
```

Optional settings with their defaults:
```python
GAR_ACTIVE_USER_REDIRECT = "/"  # Redirect after successful login
GAR_INACTIVE_USER_REDIRECT = "/"  # Redirect for inactive users
GAR_QUERY_STRING_TRIGGER = "sso_id"  # URL parameter for SSO
```

## Management Commands

### refresh_gar_caches
Updates GAR data caches for institutions.

```shell
# Refresh all institutions
python manage.py refresh_gar_caches

# Refresh specific institution
python manage.py refresh_gar_caches --uai=0123456A
```

The command updates:
- Resource allocation data
- Subscription information

Use cases:
- Initial setup of new institutions
- Manual cache refresh
- Troubleshooting GAR integration

### refresh_gar_idents
Updates ENT IDs for all institutions from GAR.

```shell
python manage.py refresh_gar_idents
```

The command:
- Fetches the latest institution list from GAR
- Updates the ENT IDs (id_ent) for all matching institutions
- Performs updates in bulk for better performance

Use cases:
- Initial setup of new institutions
- Bulk update of ENT IDs
- Synchronizing with GAR institution list

## Testing
Run tests with pytest:
```shell
# Install test dependencies
pip install -r test_requirements.txt

# Run tests
pytest
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
