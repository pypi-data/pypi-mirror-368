import pytest
from django.utils import timezone

pytestmark = pytest.mark.django_db


class TestGARInstitutionSignals:
    def test_gar_api_not_called_for_cache_updates(self, user, mock_gar_request_response):
        # GIVEN
        institution = user.garinstitution
        
        # WHEN
        institution.allocations_cache = {"some": "data"}
        institution.allocations_cache_updated_at = timezone.now()
        institution.save(
            update_fields=["allocations_cache", "allocations_cache_updated_at"]
        )

        institution.subscription_cache = {"other": "data"}
        institution.subscription_cache_updated_at = timezone.now()
        institution.save(
            update_fields=["subscription_cache", "subscription_cache_updated_at"]
        )

        # THEN
        assert not mock_gar_request_response.called