from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms import ModelForm

from .models import GARInstitution

GAR_DISTRIBUTOR_ID = getattr(settings, "GAR_DISTRIBUTOR_ID", "")
GAR_RESOURCES_ID = getattr(settings, "GAR_RESOURCES_ID", "")
GAR_ORGANIZATION_NAME = getattr(settings, "GAR_ORGANIZATION_NAME", "")
GAR_SUBSCRIPTION_PREFIX = getattr(settings, "GAR_SUBSCRIPTION_PREFIX", "")
User = get_user_model()


class GARInstitutionForm(ModelForm):
    class Meta:
        model = GARInstitution
        fields = (
            "uai",
            "institution_name",
            "ends_at",
            "user",
            "project_code",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable ends_at field on update form
        instance = getattr(self, "instance", None)
        if instance.pk:
            self.fields["ends_at"].disabled = True

    def clean_uai(self):
        return self.cleaned_data.get("uai").upper().strip()
