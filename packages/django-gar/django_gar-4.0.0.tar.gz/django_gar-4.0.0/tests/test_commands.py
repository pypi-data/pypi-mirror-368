import pytest
from django.core.management import call_command
from django_gar.models import GARInstitution

pytestmark = pytest.mark.django_db


class TestRefreshGarCachesCommand:
    @pytest.mark.usefixtures(
        "mock_get_allocations_response",
        "mock_gar_request_response",
        "mock_gar_institution_list_response",
    )
    def test_refresh_caches_for_all_institutions(self, user, capsys):
        # GIVEN
        # Create another institution
        second_user = user.__class__.objects.create(username="test2")
        second_institution = GARInstitution.objects.create(
            user=second_user,
            uai="0123456A",
            institution_name="Test Institution 2",
            subscription_id="test_id_2",
        )

        # WHEN
        call_command("refresh_gar_caches")
        captured = capsys.readouterr()

        # THEN
        assert "Refreshing caches for 2 institution(s)..." in captured.out
        assert f"Processing {user.garinstitution.uai}..." in captured.out
        assert f"Processing {second_institution.uai}..." in captured.out
        assert "Done!" in captured.out

    @pytest.mark.usefixtures(
        "mock_get_allocations_response",
        "mock_gar_request_response",
        "mock_gar_institution_list_response",
        "mock_get_gar_subscription",
    )
    def test_refresh_caches_for_specific_uai(self, user, capsys):
        # GIVEN
        # Create another institution
        second_user = user.__class__.objects.create(username="test2")
        GARInstitution.objects.create(
            user=second_user,
            uai="0123456A",
            institution_name="Test Institution 2",
            subscription_id="test_id_2",
        )

        # WHEN
        call_command("refresh_gar_caches", uai=user.garinstitution.uai)
        captured = capsys.readouterr()

        # THEN
        assert "Refreshing caches for 1 institution(s)..." in captured.out
        assert f"Processing {user.garinstitution.uai}..." in captured.out
        assert "Done!" in captured.out

    def test_refresh_caches_with_invalid_uai(self, capsys):
        # WHEN
        call_command("refresh_gar_caches", uai="INVALID")
        captured = capsys.readouterr()

        # THEN
        assert 'No institution found with UAI "INVALID"' in captured.out
        assert "Done!" not in captured.out

    @pytest.mark.usefixtures(
        "mock_get_allocations_response",
        "mock_gar_request_response",
        "mock_gar_institution_list_response",
        "mock_get_gar_subscription",
    )
    def test_refresh_caches_updates_institution_data(self, user):
        # GIVEN
        institution = user.garinstitution
        assert institution.allocations_cache is None
        assert institution.subscription_cache is None

        # WHEN
        call_command("refresh_gar_caches", uai=institution.uai)

        # THEN
        institution.refresh_from_db()
        assert institution.allocations_cache["cumulAffectationEnseignant"] == "226"
        assert "abonnement" in institution.subscription_cache


class TestRefreshGarIdentsCommand:
    @pytest.mark.usefixtures(
        "mock_gar_institution_list_response", "mock_gar_request_response"
    )
    def test_refresh_idents_updates_institutions(self, user):
        # GIVEN
        institution = user.garinstitution
        institution.uai = "0941295X"
        institution.id_ent = None
        institution.save()

        # Create another institution
        second_user = user.__class__.objects.create(username="test2")
        second_institution = GARInstitution.objects.create(
            user=second_user,
            uai="0123456A",  # This one won't be found in GAR
            institution_name="Test Institution 2",
            subscription_id="test_id_2",
        )

        # WHEN
        call_command("refresh_gar_idents")

        # THEN
        institution.refresh_from_db()
        second_institution.refresh_from_db()
        assert institution.id_ent == "123456"
        assert second_institution.id_ent is None
