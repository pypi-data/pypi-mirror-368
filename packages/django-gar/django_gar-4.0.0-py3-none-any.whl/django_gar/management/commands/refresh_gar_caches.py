from django.core.management.base import BaseCommand
from django_gar.models import GARInstitution


class Command(BaseCommand):
    help = "Refresh GAR subscription, allocations and ID ENT caches for institutions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--uai",
            help="Refresh caches only for this UAI",
        )

    def handle(self, *args, **options):
        queryset = GARInstitution.objects.all()
        if options["uai"]:
            queryset = queryset.filter(uai=options["uai"])
            if not queryset.exists():
                self.stdout.write(
                    self.style.ERROR(
                        f'No institution found with UAI "{options["uai"]}"'
                    )
                )
                return

        count = queryset.count()
        self.stdout.write(f"Refreshing caches for {count} institution(s)...")

        for institution in queryset:
            self.stdout.write(f"Processing {institution.uai}...")

            institution.refresh_subscription_cache()
            institution.refresh_allocations_cache()

        self.stdout.write(self.style.SUCCESS("Done!"))
