import logging
import urllib.parse

from bs4 import BeautifulSoup

from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .models import GARSession

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        return TemplateResponse(request, "django_gar/logout.html", {})

    def post(self, request, *args, **kwargs):
        """x-www-form-urlencoded body to decode from GARrequest logout"""
        body = request.body.decode("utf-8")

        logger.info(body)

        data = urllib.parse.parse_qs(body)["logoutRequest"][0]

        soup = BeautifulSoup(data, "xml")
        session_index = soup.find("samlp:SessionIndex")

        if session_index:
            try:
                gar_session = GARSession.objects.get(ticket=session_index.text)
                store = SessionStore(session_key=gar_session.session_key)
                logger.info(f"request GAR logout {gar_session.session_key}")

                store["gar_logout"] = True
                store.save()
            except GARSession.DoesNotExist:
                logger.info(
                    "cannot log out from GAR session as it does not exist anymore"
                )

        return HttpResponse(status=204)
