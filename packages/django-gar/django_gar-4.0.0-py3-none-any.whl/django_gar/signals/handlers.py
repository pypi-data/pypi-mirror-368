import time
import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from defusedxml import ElementTree as ET

from ..models import GARInstitution
from ..gar import (
    delete_gar_subscription,
    get_gar_certificate,
    get_gar_headers,
    get_gar_request_url,
    get_gar_institution_list,
)

logger = logging.getLogger(__name__)

GAR_DISTRIBUTOR_ID = getattr(settings, "GAR_DISTRIBUTOR_ID", "")
GAR_RESOURCES_ID = getattr(settings, "GAR_RESOURCES_ID", "")
GAR_ORGANIZATION_NAME = getattr(settings, "GAR_ORGANIZATION_NAME", "")
GAR_SUBSCRIPTION_PREFIX = getattr(settings, "GAR_SUBSCRIPTION_PREFIX", "")


@receiver(post_delete, sender=GARInstitution, dispatch_uid="delete_subscription_in_gar")
def delete_subscription_in_gar(sender, instance, **kwargs):
    delete_gar_subscription(instance.subscription_id)


def _get_gar_start_date(instance, http_method):
    """Get the start date for GAR subscription"""
    if http_method == "POST":
        uai = instance.uai.upper().strip()
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
        cert = get_gar_certificate()
        headers = get_gar_headers()
        response = requests.request(
            "GET",
            "https://abonnement.gar.education.fr/abonnements",
            data=data,
            cert=cert,
            headers=headers,
        )
        soup = BeautifulSoup(response.text, "lxml")
        subscriptions = soup.findAll("abonnement")
        for subscription in subscriptions:
            if subscription.find("idabonnement").text == instance.subscription_id:
                return subscription.find("debutvalidite").text

    return datetime.now().isoformat()


def _get_gar_data_to_send(instance, http_method=None):
    """Generate XML data for GAR subscription"""
    uai = instance.uai.upper().strip()
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <abonnement xmlns="http://www.atosworldline.com/wsabonnement/v1.0/">
       <idAbonnement>{subscription_id}</idAbonnement>
       <idDistributeurCom>{distributor_id}</idDistributeurCom>
       <idRessource>{resources_id}</idRessource>
       <typeIdRessource>ark</typeIdRessource>
       <libelleRessource>{organization_name}</libelleRessource>
       <debutValidite>{start_date}</debutValidite>
       <finValidite>{end_date}T23:59:59</finValidite>
       <uaiEtab>{uai}</uaiEtab>
       <categorieAffectation>transferable</categorieAffectation>
       <typeAffectation>ETABL</typeAffectation>
       <nbLicenceGlobale>ILLIMITE</nbLicenceGlobale>
       <publicCible>ELEVE</publicCible>
       <publicCible>ENSEIGNANT</publicCible>
       <publicCible>DOCUMENTALISTE</publicCible>
       <publicCible>AUTRE PERSONNEL</publicCible>
       <codeProjetRessource>{project_code}</codeProjetRessource>
    </abonnement>""".format(
        subscription_id=instance.subscription_id,
        distributor_id=GAR_DISTRIBUTOR_ID,
        resources_id=GAR_RESOURCES_ID,
        organization_name=GAR_ORGANIZATION_NAME,
        start_date=_get_gar_start_date(instance, http_method),
        end_date=instance.ends_at,
        uai=uai,
        project_code=instance.project_code,
    )

    if not instance.project_code:
        xml = xml.replace(
            f"<codeProjetRessource>{instance.project_code}</codeProjetRessource>", ""
        )

    if http_method == "POST":
        xml = xml.replace(f"<uaiEtab>{uai}</uaiEtab>", "")

    return xml


def _get_response_from_gar(instance, http_method):
    """Send request to GAR API"""
    url = get_gar_request_url(instance.subscription_id)
    cert = get_gar_certificate()
    headers = get_gar_headers()
    response = requests.request(
        http_method,
        url,
        data=_get_gar_data_to_send(instance, http_method=http_method),
        cert=cert,
        headers=headers,
    )

    if response.status_code == 409 and "existe deja" in response.text:
        response = _get_response_from_gar(instance, http_method="POST")

    return response


@receiver(pre_save, sender=GARInstitution, dispatch_uid="handle_gar_subscription")
def handle_gar_subscription(sender, instance, **kwargs):
    """Handle GAR subscription creation/update before saving the instance"""
    # Skip if we're only updating cache fields
    if kwargs.get('update_fields') == {'allocations_cache', 'allocations_cache_updated_at'} or \
       kwargs.get('update_fields') == {'subscription_cache', 'subscription_cache_updated_at'}:
        logger.info(f"GAR subscription caches for {instance.uai} updated")
        return

    if not instance.subscription_id:
        instance.subscription_id = f"{GAR_SUBSCRIPTION_PREFIX}{int(time.time())}"

    # Check if this is a new instance or an update
    if not instance.pk:
        response = _get_response_from_gar(instance, http_method="PUT")
        if response.status_code not in [201, 200]:
            logger.error(response.text)
    else:
        response = _get_response_from_gar(instance, http_method="POST")
        if response.status_code != 200:
            logger.error(response.text)

    logger.info(f"GAR subscription {instance.uai} updated with status code {response.status_code}")


@receiver(pre_save, sender=GARInstitution, dispatch_uid="get_id_ent")
def get_id_ent(sender, instance, **kwargs):
    if instance.pk:
        return

    institution_list = get_gar_institution_list()
    xml_data = institution_list.content
    root = ET.fromstring(xml_data)
    namespace = {"ns": "http://www.atosworldline.com/listEtablissement/v1.0/"}
    id_ent = None
    for etablissement in root.findall("ns:etablissement", namespace):
        uai = etablissement.find("ns:uai", namespace)
        if uai is not None and uai.text == instance.uai:
            # Found the correct UAI, now get the idENT
            id_ent_object = etablissement.find("ns:idENT", namespace)
            id_ent = id_ent_object.text if id_ent_object is not None else None
            continue
    if id_ent:
        instance.id_ent = id_ent
    else:
        logger.error(f"id ent not found for uai {instance.uai}")
