import pytest
import requests
from urllib.parse import urlencode

from django_gar.exceptions import DjangoGARException
from django_gar.gar import (
    get_gar_subscription,
    get_allocations,
    GAR_ALLOCATIONS_URL,
    get_gar_subscription_end_date,
    get_gar_institution_list,
    delete_gar_subscription,
    GAR_BASE_SUBSCRIPTION_URL,
)

pytestmark = pytest.mark.django_db()


class TestGetGarSubscription:
    def test_with_subscription_in_response(self, user, mocker, response_from_gar):
        # GIVEN
        user.garinstitution.uai = "0561622J"
        user.garinstitution.subscription_id = "briefeco_1630592291"
        mocker.patch("django_gar.signals.handlers.handle_gar_subscription")
        with open(
            "tests/fixtures/get_gar_subscription_response.xml", "r"
        ) as xml_response:
            mock_request = mocker.patch.object(
                requests,
                "request",
                return_value=response_from_gar(200, xml_response.read()),
            )

        # WHEN
        response = get_gar_subscription(
            user.garinstitution.uai, user.garinstitution.subscription_id
        )

        # THEN
        assert mock_request.call_count == 1
        assert response

    def test_with_wrong_subscription_id(self, user, mocker, response_from_gar):
        # GIVEN
        user.garinstitution.uai = "0561622J"
        mocker.patch("django_gar.signals.handlers.handle_gar_subscription")
        with open(
            "tests/fixtures/get_gar_subscription_response.xml", "r"
        ) as xml_response:
            mock_request = mocker.patch.object(
                requests,
                "request",
                return_value=response_from_gar(200, xml_response.read()),
            )

        # WHEN
        response = get_gar_subscription(
            user.garinstitution.uai, user.garinstitution.subscription_id
        )

        # THEN
        assert mock_request.call_count == 1
        assert not response

    def test_with_status_code_not_200(self, user, mocker, response_from_gar):
        # GIVEN
        user.garinstitution.subscription_id = "briefeco_1630592291"
        mocker.patch("django_gar.signals.handlers.handle_gar_subscription")
        with open(
            "tests/fixtures/get_gar_subscription_response.xml", "r"
        ) as xml_response:
            mock_request = mocker.patch.object(
                requests,
                "request",
                return_value=response_from_gar(404, xml_response.read()),
            )

        # WHEN / THEN
        with pytest.raises(DjangoGARException):
            get_gar_subscription(
                user.garinstitution.uai, user.garinstitution.subscription_id
            )

        assert mock_request.call_count == 1

    def test_with_empty_response(self, user, mocker, response_from_gar):
        # GIVEN
        user.garinstitution.subscription_id = "briefeco_1630592291"
        mocker.patch("django_gar.signals.handlers.handle_gar_subscription")
        mock_request = mocker.patch.object(
            requests,
            "request",
            return_value=response_from_gar(200, ""),
        )

        # WHEN
        response = get_gar_subscription(
            user.garinstitution.uai, user.garinstitution.subscription_id
        )

        # THEN
        assert mock_request.call_count == 1
        assert not response


class TestGetGarSubscriptionEndDate:
    def test_with_valid_subscription(self, user, mocker, response_from_gar):
        # GIVEN
        expected_date = "2024-12-31"
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <abonnements xmlns="http://www.atosworldline.com/wsabonnement/v1.0/">
            <abonnement>
                <idabonnement>briefeco_1630592291</idabonnement>
                <finvalidite>2024-12-31</finvalidite>
            </abonnement>
        </abonnements>"""
        mock_request = mocker.patch.object(
            requests,
            "request",
            return_value=response_from_gar(200, xml_content),
        )

        # WHEN
        end_date = get_gar_subscription_end_date(
            user.garinstitution.uai, "briefeco_1630592291"
        )

        # THEN
        assert mock_request.called_once()
        assert end_date == expected_date

    def test_with_no_subscription(self, user, mocker, response_from_gar):
        # GIVEN
        mock_request = mocker.patch.object(
            requests,
            "request",
            return_value=response_from_gar(200, "<abonnements></abonnements>"),
        )

        # WHEN
        end_date = get_gar_subscription_end_date(
            user.garinstitution.uai, "non_existent_id"
        )

        # THEN
        assert mock_request.called_once()
        assert end_date is None


class TestGetAllocations:
    def test_get_allocations_no_params(self):
        # GIVEN / WHEN
        with pytest.raises(DjangoGARException) as exc_info:
            get_allocations()

        # THEN
        assert exc_info.value.status_code == 400
        assert (
            exc_info.value.message
            == "At least one of subscription_id or project_code is mandatory"
        )

    def test_get_allocations_both_params(self):
        # GIVEN / WHEN
        with pytest.raises(DjangoGARException) as exc_info:
            get_allocations(subscription_id="123", project_code="ABC")

        # THEN
        assert exc_info.value.status_code == 400
        assert (
            exc_info.value.message
            == "Cannot set subscription_id and project_code at the same time"
        )

    def test_get_allocations_with_subscription_id(
        self, user, mock_get_allocations_request
    ):
        # WHEN
        response = get_allocations(subscription_id=user.garinstitution.subscription_id)

        # THEN
        mock_get_allocations_request.assert_called_once_with(
            "GET",
            f"{GAR_ALLOCATIONS_URL}?idAbonnement={user.garinstitution.subscription_id}",
            cert=("", ""),
        )
        assert response.status_code == 200

    def test_get_allocations_with_project_code(self, mock_get_allocations_request):
        # WHEN
        response = get_allocations(project_code="DUMMY")

        # THEN
        mock_get_allocations_request.assert_called_once_with(
            "GET", f"{GAR_ALLOCATIONS_URL}?codeProjetRessource=DUMMY", cert=("", "")
        )
        assert response.status_code == 200

    def test_with_subscription_id(self, mocker, response_from_gar):
        # GIVEN
        subscription_id = "test_sub_id"
        mock_request = mocker.patch.object(
            requests,
            "request",
            return_value=response_from_gar(200, "response"),
        )

        # WHEN
        response = get_allocations(subscription_id=subscription_id)

        # THEN
        assert mock_request.call_count == 1
        expected_url = (
            f"{GAR_ALLOCATIONS_URL}?{urlencode({'idAbonnement': subscription_id})}"
        )
        mock_request.assert_called_with(
            "GET",
            expected_url,
            cert=mocker.ANY,
        )

    def test_with_project_code(self, mocker, response_from_gar):
        # GIVEN
        project_code = "test_project"
        mock_request = mocker.patch.object(
            requests,
            "request",
            return_value=response_from_gar(200, "response"),
        )

        # WHEN
        response = get_allocations(project_code=project_code)

        # THEN
        assert mock_request.call_count == 1
        expected_url = (
            f"{GAR_ALLOCATIONS_URL}?{urlencode({'codeProjetRessource': project_code})}"
        )
        mock_request.assert_called_with(
            "GET",
            expected_url,
            cert=mocker.ANY,
        )

    def test_with_no_parameters(self):
        # WHEN/THEN
        with pytest.raises(DjangoGARException) as exc:
            get_allocations()
        assert "At least one of subscription_id or project_code is mandatory" in str(
            exc.value
        )

    def test_with_both_parameters(self):
        # WHEN/THEN
        with pytest.raises(DjangoGARException) as exc:
            get_allocations(subscription_id="test", project_code="test")
        assert "Cannot set subscription_id and project_code at the same time" in str(
            exc.value
        )


class TestDeleteGarSubscription:
    def test_successful_deletion(self, user, mocker, response_from_gar):
        # GIVEN
        user.garinstitution.subscription_id = "test_subscription"
        mock_request = mocker.patch.object(
            requests,
            "delete",
            return_value=response_from_gar(200, "Successfully deleted"),
        )

        # WHEN
        delete_gar_subscription(user.garinstitution.subscription_id)

        # THEN
        assert mock_request.call_count == 1
        mock_request.assert_called_with(
            f"{GAR_BASE_SUBSCRIPTION_URL}test_subscription",
            cert=mocker.ANY,
            headers=mocker.ANY,
            timeout=30,
        )

    def test_failed_deletion(self, user, mocker, response_from_gar):
        # GIVEN
        user.garinstitution.subscription_id = "test_subscription"
        mock_request = mocker.patch.object(
            requests,
            "delete",
            return_value=response_from_gar(404, "Not found"),
        )

        # WHEN
        delete_gar_subscription(user.garinstitution.subscription_id)

        # THEN
        assert mock_request.call_count == 1
        mock_request.assert_called_with(
            f"{GAR_BASE_SUBSCRIPTION_URL}test_subscription",
            cert=mocker.ANY,
            headers=mocker.ANY,
            timeout=30,
        )


class TestGetGarInstitutionList:
    def test_successful_list_retrieval(self, mocker, response_from_gar):
        # GIVEN
        mock_request = mocker.patch.object(
            requests,
            "request",
            return_value=response_from_gar(200, "Institution list"),
        )

        # WHEN
        response = get_gar_institution_list()

        # THEN
        assert mock_request.call_count == 1
        assert response.status_code == 200
