import requests
import logging

from bs4 import BeautifulSoup
from urllib.parse import urlencode

from django.conf import settings

from .exceptions import DjangoGARException

logger = logging.getLogger(__name__)

GAR_SUBSCRIPTION_PREFIX = getattr(settings, "GAR_SUBSCRIPTION_PREFIX", "")
GAR_BASE_SUBSCRIPTION_URL = getattr(
    settings, "GAR_BASE_SUBSCRIPTION_URL", "https://abonnement.gar.education.fr/"
)
GAR_ALLOCATIONS_URL = getattr(
    settings,
    "GAR_ALLOCATIONS_URL",
    "https://decompte-affectations.gar.education.fr/decompteaffectations",
)
GAR_DISTRIBUTOR_ID = getattr(settings, "GAR_DISTRIBUTOR_ID", "")

GAR_CERTIFICATE_PATH = getattr(settings, "GAR_CERTIFICATE_PATH", "")
GAR_KEY_PATH = getattr(settings, "GAR_KEY_PATH", "")


def delete_gar_subscription(subscription_id):
    url = get_gar_request_url(subscription_id)
    cert = get_gar_certificate()
    headers = get_gar_headers()
    requests.delete(url, cert=cert, headers=headers, timeout=30)


def get_gar_request_url(subscription_id):
    base_url = GAR_BASE_SUBSCRIPTION_URL
    url = "{}{}".format(base_url, subscription_id)
    return url


def get_gar_certificate():
    cert = (GAR_CERTIFICATE_PATH, GAR_KEY_PATH)
    return cert


def get_gar_headers():
    headers = {"Content-Type": "application/xml"}
    return headers


def get_gar_subscription(uai, subscription_id):
    data = """<?xml version="1.0" encoding="UTF-8"?>
        <filtres xmlns="http://www.atosworldline.com/wsabonnement/v1.0/">
              <filtre>
                    <filtreNom>idDistributeurCom</filtreNom>
                    <filtreValeur>{distributor_id}</filtreValeur>
              </filtre> 
              <filtre>
                    <filtreNom>uaiEtab</filtreNom>
                    <filtreValeur>{uai}</filtreValeur>
              </filtre> 
        </filtres>""".format(
        distributor_id=GAR_DISTRIBUTOR_ID, uai=uai
    )
    response = requests.request(
        "GET",
        "{}{}".format(GAR_BASE_SUBSCRIPTION_URL, "abonnements"),
        data=data,
        cert=get_gar_certificate(),
        headers=get_gar_headers(),
    )

    if response.status_code != 200:
        raise DjangoGARException(
            status_code=response.status_code, message=response.text
        )

    soup = BeautifulSoup(response.text, "lxml")
    subscriptions = soup.findAll("abonnement")
    for subscription in subscriptions:
        if subscription.find("idabonnement").text == subscription_id:
            return subscription

    return None


def get_gar_subscription_end_date(uai, subscription_id):
    subscription = get_gar_subscription(uai, subscription_id)

    if subscription:
        return subscription.find("finvalidite").text

    return None


def get_gar_institution_list():
    return requests.request(
        "GET",
        f"{GAR_BASE_SUBSCRIPTION_URL}etablissements/etablissements.xml",
        cert=get_gar_certificate(),
        headers=get_gar_headers(),
    )


def get_allocations(subscription_id=None, project_code=None):
    if not subscription_id and not project_code:
        raise DjangoGARException(
            status_code=400,
            message="At least one of subscription_id or project_code is mandatory",
        )
    elif subscription_id and project_code:
        raise DjangoGARException(
            status_code=400,
            message="Cannot set subscription_id and project_code at the same time",
        )

    params = {"codeProjetRessource": project_code}
    if subscription_id:
        params = {"idAbonnement": subscription_id}

    return requests.request(
        "GET",
        f"{GAR_ALLOCATIONS_URL}?{urlencode(params)}",
        cert=get_gar_certificate(),
    )
