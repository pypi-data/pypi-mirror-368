import pytest

from django.conf import settings

from django_gar.middleware import GARMiddleware

pytestmark = pytest.mark.django_db

GAR_QUERY_STRING_TRIGGER = settings.GAR_QUERY_STRING_TRIGGER


class TestGARMiddleware:
    @staticmethod
    def test_init():
        """Testing the __init__ method"""
        # WHEN
        cas_middleware = GARMiddleware("dump_response")

        # THEN
        assert cas_middleware.get_response == "dump_response"

    def test_no_uai_no_ticket(self, request_builder):
        """Testing the middleware if not a connection to GAR"""
        # GIVEN
        cas_middleware = GARMiddleware(request_builder.get)

        # WHEN
        response = cas_middleware(request_builder.get())

        # THEN
        assert cas_middleware.get_response().path == "/"
        assert GAR_QUERY_STRING_TRIGGER not in response.GET
        assert "ticket" not in response.GET

    def test_when_uai_number(self, user, request_builder):
        """Testing the __call__ method with uai_number in url"""
        # GIVEN
        uai_number = "GAR"
        query_params = "?{}={}".format(GAR_QUERY_STRING_TRIGGER, uai_number)
        request = request_builder.get(query_params)
        cas_middleware = GARMiddleware(request)

        # WHEN
        response = cas_middleware(request)

        # THEN
        assert settings.GAR_BASE_URL.format(uai_number) in response.url

    def test_when_uai_number_is_gar(self, request_builder):
        """Testing the __call__ method with uai_number in url and is gar"""
        # GIVEN
        query_params = "?{}={}".format(GAR_QUERY_STRING_TRIGGER, "gar")
        request = request_builder.get(query_params)
        cas_middleware = GARMiddleware(request)

        # WHEN
        response = cas_middleware(request)

        # THEN
        assert settings.GAR_BASE_URL in response.url

    def test_when_cas_ticket_valid(self, mock_validate_valid_ticket, request_builder):
        """
        Testing the __call__ method with valid cas_ticket in url and user
        has access (is_active is True)
        """
        # GIVEN
        cas_ticket = "this-is-a-ticket"
        query_params = "?ticket={}".format(cas_ticket)
        request = request_builder.get(path=query_params)
        request.session["is_gar"] = True
        cas_middleware = GARMiddleware(request_builder.get)

        # WHEN
        response = cas_middleware(request)

        # THEN
        assert mock_validate_valid_ticket.call_count == 1
        assert response.url == settings.GAR_ACTIVE_USER_REDIRECT

    def test_when_cas_ticket_valid_and_grain(
        self, mock_validate_valid_ticket, request_builder
    ):
        """
        Redirect the user to a specific url using the 'grain' query string
        """
        # GIVEN
        cas_ticket = "this-is-a-ticket"
        grain_url = "https://www.dummy.com"
        query_params = "?ticket={}&grain={}".format(cas_ticket, grain_url)
        request = request_builder.get(path=query_params)
        request.session["is_gar"] = True
        cas_middleware = GARMiddleware(request_builder.get)

        # WHEN
        response = cas_middleware(request)

        # THEN
        assert mock_validate_valid_ticket.call_count == 1
        assert response.url == grain_url

    def test_when_cas_ticket_invalid(
        self, mock_validate_invalid_ticket, request_builder
    ):
        """
        Testing the __call__ method with invalid cas_ticket in url and user
        has access (is_active is True)
        """
        # GIVEN
        cas_ticket = "this-is-a-ticket"
        query_params = "/?ticket={}".format(cas_ticket)
        request = request_builder.get(query_params)
        request.session["is_gar"] = True
        cas_middleware = GARMiddleware(request_builder.get)

        # WHEN
        response = cas_middleware(request)

        # THEN
        assert response.status_code == 302
        assert mock_validate_invalid_ticket.call_count == 1
        assert response.url == settings.GAR_INACTIVE_USER_REDIRECT

    def test_validate_ticket(self, mock_verification_response, request_builder):
        # GIVEN
        request = request_builder.get()
        request.session["is_gar"] = True

        # WHEN
        mock_verification_response.get()
        cas_middleware = GARMiddleware(request_builder.get)
        uai_numbers = cas_middleware.validate_ticket(request, "dummy-ticket")

        # THEN
        assert "0561641E" in uai_numbers
        mock_verification_response.assert_called_once()

    def test_validate_ticket_parse_error(
        self, mock_verification_response_error, request_builder
    ):
        # GIVEN
        request = request_builder.get()
        request.session["is_gar"] = True

        # WHEN
        cas_middleware = GARMiddleware(request_builder.get)
        response = cas_middleware.validate_ticket(request, "dummy-ticket")

        # THEN
        assert not response
