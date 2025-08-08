import csv

from django.urls import path
from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.utils.html import format_html

from .gar import get_allocations
from .forms import GARInstitutionForm
from .models import GARInstitution

GAR_RESOURCES_ID = getattr(settings, "GAR_RESOURCES_ID", "")


@admin.register(GARInstitution)
class GARInstitutionAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
    list_display = ("institution_name", "user", "uai", "ends_at")
    list_select_related = ("user",)
    readonly_fields = (
        "id_ent",
        "subscription_id",
        "gar_subscription_response",
        "get_allocations",
    )
    ordering = ("institution_name",)
    search_fields = ("institution_name", "user__email", "uai", "project_code")
    list_filter = ["project_code"]
    form = GARInstitutionForm
    change_list_template = "admin/django_gar/change_list.html"

    @admin.display(description="Etat de l'abonnement dans le GAR")
    def gar_subscription_response(self, obj):
        if not obj.uai:
            return ""

        # Update cache if needed
        if not obj.subscription_cache:
            obj.refresh_subscription_cache()

        if not obj.subscription_cache:
            return (
                "L'abonnement n'existe pas dans le GAR. "
                "Vous pouvez le supprimer et en créer un nouveau."
            )

        response = ""
        for key, value in obj.subscription_cache.items():
            response += f"{key} : {value}<br/>"

        return format_html(f"<code>{response}</code>")

    @admin.display(description="Etat des affectations")
    def get_allocations(self, obj):
        if not obj.uai or not obj.subscription_id:
            return ""

        # Update cache if needed
        if not obj.allocations_cache:
            obj.refresh_allocations_cache()

        if not obj.allocations_cache:
            return "L'établissement n'a pas encore affecté la ressource. Les informations fournies par le webservice font l'objet d'un traitement asynchrone et sont par conséquent actualisées quotidiennement. Il peut être constaté une latence dans la prise en compte de changements en cas d'affectations / récupérations de licences au sein d'une même journée."

        allocations = ""
        for key, value in obj.allocations_cache.items():
            allocations += f"{key} : {value}<br/>"

        return format_html(f"<code>{allocations}</code>")

    def get_urls(self):
        urlpatterns = super().get_urls()

        allocations_report_url = [
            path(
                "allocations-report/generate/",
                self.admin_site.admin_view(self.allocations_report),
                name="{app_label}_{model_name}_generate_allocations_report".format(
                    app_label=self.model._meta.app_label,
                    model_name=self.model._meta.model_name,
                ),
            )
        ]

        return allocations_report_url + urlpatterns

    def allocations_report(self, request):
        """Generate a CSV report of allocations for all institutions"""
        # Headers for the CSV
        headers = [
            "InstitutionName",
            "UAI",
            "idAbonnement",
            "codeProjetRessource",
            "idRessource",
            "cumulAffectationEleve",
            "cumulAffectationEnseignant",
            "cumulAffectationDocumentaliste",
            "cumulAffectationAutrePersonnel",
        ]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="rapport_affectations.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(headers)

        # Get all institutions
        institutions = self.model.objects.all()

        # Write data for each institution
        for institution in institutions:
            allocations = institution.allocations_cache or {}
            writer.writerow(
                [
                    institution.institution_name,
                    institution.uai,
                    institution.subscription_id,
                    institution.project_code,
                    settings.GAR_RESOURCES_ID,
                    allocations.get("cumulAffectationEleve", "0"),
                    allocations.get("cumulAffectationEnseignant", "0"),
                    allocations.get("cumulAffectationDocumentaliste", "0"),
                    allocations.get("cumulAffectationAutrePersonnel", "0"),
                ]
            )

        return response
