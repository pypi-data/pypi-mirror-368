import logging

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from .gar import get_allocations, get_gar_subscription


logger = logging.getLogger(__name__)
User = get_user_model()


class GARInstitution(models.Model):
    uai = models.CharField(
        "Unité Administrative Immatriculée", max_length=14, unique=True
    )
    institution_name = models.CharField("Nom de l'institution", max_length=255)
    id_ent = models.CharField("ID de l'ent", max_length=255, null=True)
    ends_at = models.DateField("Date de fin d'abonnement", null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription_id = models.CharField("id abonnement", max_length=255, unique=True)
    project_code = models.CharField(
        "Code de projet ressources", max_length=50, null=True, blank=True
    )
    allocations_cache = models.JSONField("Affectations", null=True, blank=True)
    allocations_cache_updated_at = models.DateTimeField(
        "Dernière mise à jour du cache", null=True, blank=True
    )
    subscription_cache = models.JSONField("Abonnement", null=True, blank=True)
    subscription_cache_updated_at = models.DateTimeField(
        "Dernière mise à jour du cache abonnement", null=True, blank=True
    )

    def __str__(self):
        return f"{self.institution_name} ({self.uai})"

    def refresh_allocations_cache(self):
        if not self.subscription_id:
            return

        response = get_allocations(subscription_id=self.subscription_id)

        self.allocations_cache_updated_at = timezone.now()

        if response.status_code == 200:
            # Parse CSV data into a dictionary
            csv_content = response.content.decode("utf-8")
            lines = csv_content.splitlines()

            if len(lines) > 1:  # If we have header and data
                headers = lines[0].split(";")
                values = lines[1].split(";")  # We take the first data line
                self.allocations_cache = dict(zip(headers, values))
            else:
                self.allocations_cache = None

            logger.info("Allocations cache updated successfully.")
        else:
            self.allocations_cache = None
            logger.error(
                f"Failed to refresh allocations cache. Status code: {response.status_code}, Response: {response.text}"
            )

        self.save(
            update_fields=["allocations_cache", "allocations_cache_updated_at"],
        )

    def refresh_subscription_cache(self):
        if not self.uai or not self.subscription_id:
            return

        subscription = get_gar_subscription(self.uai, self.subscription_id)

        self.subscription_cache_updated_at = timezone.now()

        if subscription:
            self.subscription_cache = {
                element.name: element.text for element in subscription.find_all()
            }
            self.save(
                update_fields=["subscription_cache", "subscription_cache_updated_at"]
            )
            logger.info("Subscription cache updated successfully.")
        else:
            self.subscription_cache = None
            logger.error(f"No subscription found in GAR for {self.uai}.")

        self.save(update_fields=["subscription_cache", "subscription_cache_updated_at"])


class GARSession(models.Model):
    """Store GAR active session. This will help us to delete user sessions when the user log out from the GAR"""

    ticket = models.CharField("CAS ticket", max_length=255, unique=True)
    session_key = models.CharField("Django session key", max_length=255, unique=True)

    def __str__(self):
        return f"ticket: {self.ticket} - session_key: {self.session_key}"
