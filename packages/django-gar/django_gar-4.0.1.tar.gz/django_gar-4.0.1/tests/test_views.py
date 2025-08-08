import logging
import pytest

from django_gar.views import LogoutView

pytestmark = pytest.mark.django_db


class TestLogoutView:
    def test_with_unknown_cas_ticket(self, mocker, logout_body, request_builder):
        # GIVEN
        mock_logger = mocker.patch.object(logging.getLogger("django_gar.views"), "info")
        request = request_builder.post(data=logout_body)

        # WHEN
        response = LogoutView.as_view()(request)

        # THEN
        assert response.status_code == 204
        assert mock_logger.call_count == 2
        logger_messages = [call[0] for call, _ in mock_logger.call_args_list]
        assert logger_messages[0] == logout_body
        assert (
            logger_messages[1]
            == "cannot log out from GAR session as it does not exist anymore"
        )

    def test_with_existing_gar_session(
        self, mocker, logout_body, request_builder, gar_session
    ):
        # GIVEN
        mock_logger = mocker.patch.object(logging.getLogger("django_gar.views"), "info")
        request = request_builder.post(data=logout_body)

        # WHEN
        response = LogoutView.as_view()(request)

        # THEN
        assert response.status_code == 204
        assert mock_logger.call_count == 2
        logger_messages = [call[0] for call, _ in mock_logger.call_args_list]
        assert logger_messages[0] == logout_body
        assert logger_messages[1] == f"request GAR logout {gar_session.session_key}"
