from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):

    help = "Create and configure GeoCareerGo admin roles"

    def handle(self, *args, **options):

        # ==================================================
        # CONTENT ADMIN
        # ==================================================

        content_admin, created = Group.objects.get_or_create(
            name="Content Admin"
        )

        # Start with no permissions
        content_admin.permissions.clear()

        # Models that Content Admin can manage
        allowed_models = [
            ("jobs", "job"),
            ("notes", "note"),
            ("exam_tests", "test"),
            ("exam_tests", "question"),
        ]

        # Actions allowed
        allowed_actions = [
            "add",
            "change",
            "view",
        ]

        permissions_added = 0

        for app_label, model_name in allowed_models:

            for action in allowed_actions:

                codename = f"{action}_{model_name}"

                try:

                    permission = Permission.objects.get(
                        content_type__app_label=app_label,
                        content_type__model=model_name,
                        codename=codename
                    )

                    content_admin.permissions.add(
                        permission
                    )

                    permissions_added += 1

                except Permission.DoesNotExist:

                    self.stdout.write(
                        self.style.WARNING(
                            f"Permission not found: "
                            f"{app_label}.{codename}"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                "Content Admin group configured successfully."
            )
        )

        self.stdout.write(
            f"Permissions added: {permissions_added}"
        )

        self.stdout.write(
            "Super Admin remains unrestricted."
        )