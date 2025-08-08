import pytest

from django_gar.apps import DjangoGarConfig

pytestmark = pytest.mark.django_db


class TestDjangoGarConfig:
    @staticmethod
    def test_apps():
        assert "django_gar" in DjangoGarConfig.name
