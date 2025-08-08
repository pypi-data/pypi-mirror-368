import pytest
import requests
from django.core.exceptions import ValidationError
from django_gar.forms import GARInstitutionForm
import datetime
import logging

pytestmark = pytest.mark.django_db


class TestGARInstitutionForm:
    def test_clean_uai_strips_and_uppercases(self):
        # GIVEN
        form = GARInstitutionForm(
            data={
                "uai": " abc ",
                "institution_name": "Test Institution",
                "ends_at": datetime.datetime.today(),
                "subscription_id": "test-123",
            }
        )

        # WHEN
        form.is_valid()  # This populates cleaned_data
        cleaned_uai = form.clean_uai()

        # THEN
        assert cleaned_uai == "ABC"

    def test_form_works_with_gar_when_creating_instance(
        self, form_data, mocker, response_from_gar
    ):
        # GIVEN
        mock_request = mocker.patch.object(
            requests,
            "request",
            return_value=response_from_gar(201, "dummy response message"),
        )

        # WHEN
        form = GARInstitutionForm(data=form_data().data)
        form.is_valid()
        form.save()

        # THEN
        assert mock_request.called_once()
        assert form.is_valid()

    def test_form_error_with_gar_when_creating_instance(
        self, form_data, mocker, response_from_gar, caplog
    ):
        # GIVEN
        mocker.patch.object(
            requests,
            "request",
            return_value=response_from_gar(400, "dummy error message"),
        )

        # WHEN
        form = GARInstitutionForm(data=form_data().data)
        form.is_valid()
        with caplog.at_level(logging.INFO):
            form.save()

        # THEN
        assert f"dummy error message" in caplog.records[0].message

    def test_form_works_with_gar_when_try_creating_instance_that_already_exists(
        self, form_data, mocker, response_from_gar
    ):
        # GIVEN
        mock_request = mocker.patch.object(
            requests,
            "request",
            side_effect=[
                response_from_gar(409, "Cette abonnement existe deja"),
                response_from_gar(200, "Hello"),
                response_from_gar(201, "OK"),
            ],
        )
        mocker.patch("django_gar.signals.handlers.handle_gar_subscription")

        # WHEN
        form = GARInstitutionForm(data=form_data().data)
        form.is_valid()
        form.save()

        # THEN
        assert mock_request.call_count == 3
        assert form.is_valid()

    def test_form_works_with_gar_when_updating_instance(
        self, form_data, mocker, response_from_gar, user
    ):
        # GIVEN
        institution = user.garinstitution
        data = form_data(garinstitution=institution).data
        mock_request = mocker.patch.object(
            requests,
            "request",
            return_value=response_from_gar(200, "dummy response message"),
        )
        mocker.patch("django_gar.signals.handlers.handle_gar_subscription")

        # WHEN
        form = GARInstitutionForm(instance=institution, data=data)
        form.is_valid()
        form.save()

        # THEN
        assert mock_request.called_once()
        assert form.is_valid()

    def test_form_error_with_gar_when_updating_instance(
        self, form_data, mocker, response_from_gar, user, caplog
    ):
        # GIVEN
        institution = user.garinstitution
        data = form_data(garinstitution=institution).data
        error_message = "dummy error message"
        mocker.patch.object(
            requests,
            "request",
            return_value=response_from_gar(400, error_message),
        )
        mocker.patch(
            "django_gar.signals.handlers.handle_gar_subscription",
            side_effect=ValidationError("GAR error"),
        )

        # WHEN
        form = GARInstitutionForm(instance=institution, data=data)
        form.is_valid()
        with caplog.at_level(logging.INFO):
            form.save()

        # THEN
        assert f"dummy error message" in caplog.records[0].message
