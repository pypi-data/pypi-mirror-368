import pytest

from django.db import IntegrityError

from .factories import InstitutionFactory

pytestmark = pytest.mark.django_db


class TestGARInstitutionModel(object):
    def test_garinstituion_has_unique_uai_number(self, user):
        uai = user.garinstitution.uai
        with pytest.raises(IntegrityError):
            InstitutionFactory(uai=uai, user=user)

    def test_garinstitution_str(self, user):
        institution = user.garinstitution
        assert str(institution) == "{} ({})".format(
            institution.institution_name, institution.uai
        )
