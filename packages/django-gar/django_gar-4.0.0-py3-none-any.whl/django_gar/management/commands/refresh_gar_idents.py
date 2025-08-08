from django.core.management.base import BaseCommand
from defusedxml import ElementTree as ET

from django_gar.models import GARInstitution
from django_gar.gar import get_gar_institution_list


class Command(BaseCommand):
    help = "Refresh ENT IDs for all institutions from GAR"

    def handle(self, *args, **options):
        institutions = GARInstitution.objects.all()

        response = get_gar_institution_list()
        if response.status_code != 200:
            self.stderr.write(
                self.style.ERROR(
                    f"Failed to get institution list for GAR: {response.status_code}"
                )
            )
            return

        # Parse XML once
        root = ET.fromstring(response.content)
        namespace = {"ns": "http://www.atosworldline.com/listEtablissement/v1.0/"}
        gar_institutions = {
            etab.find("ns:uai", namespace).text: etab.find("ns:idENT", namespace).text
            for etab in root.findall("ns:etablissement", namespace)
        }

        updates = []
        for institution in institutions:
            if institution.uai in gar_institutions:
                institution.id_ent = gar_institutions[institution.uai]
                updates.append(institution)

        GARInstitution.objects.bulk_update(updates, ["id_ent"])
