from django.apps import AppConfig


class DjangoGarConfig(AppConfig):
    name = "django_gar"

    def ready(self):
        import django_gar.signals.handlers  # noqa
