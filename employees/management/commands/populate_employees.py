import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from employees.models import Employee, Geography, Position


class Command(BaseCommand):
    help = "Populates the Employee model from existing User accounts"

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing Employee records linked to users",
        )

    def handle(self, *args, **options):
        positions = list(Position.objects.all())
        if not positions:
            self.stdout.write(
                self.style.ERROR("No Position records found. Please create some first.")
            )
            return

        users = User.objects.filter(employee__isnull=True)
        if options["overwrite"]:
            users = User.objects.all()

        created_count = 0
        skipped_count = 0

        for user in users:
            # Skip users that already have an employee record unless overwriting
            if options["overwrite"]:
                employee, created = Employee.objects.update_or_create(
                    user=user,
                    defaults=self._build_fields(user, positions),
                )
            else:
                if hasattr(user, "employee"):
                    skipped_count += 1
                    continue
                employee = Employee.objects.create(
                    user=user,
                    **self._build_fields(user, positions),
                )
                created = True

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created employee: {employee.given_name} {employee.surname}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Updated employee: {employee.given_name} {employee.surname}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created: {created_count}, Skipped: {skipped_count}"
            )
        )

    def _build_fields(self, user, positions):
        return {
            "surname": user.last_name,
            "given_name": user.first_name,
            "email": user.email,
            "position": random.choice(positions),
            "geography": Geography.objects.get(id=random.randint(1, 2)),
        }
