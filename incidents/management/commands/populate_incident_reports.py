import csv
import random
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from employees.models import Employee
from incidents.models import IncidentCategory, IncidentReport, IncidentReportCategory


class Command(BaseCommand):
    help = "Populates IncidentReport and related M2M categories from incidents_2026.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            nargs="?",
            default="incidents_2026.csv",
            help="Path to the CSV file (default: incidents_2026.csv)",
        )

    def handle(self, *args, **options):
        employees = list(Employee.objects.all())
        if not employees:
            self.stdout.write(
                self.style.ERROR(
                    "No Employee records found. Run populate_employees first."
                )
            )
            return

        categories = list(IncidentCategory.objects.all())
        if not categories:
            self.stdout.write(
                self.style.ERROR(
                    "No IncidentCategory records found. Please create some first."
                )
            )
            return

        csv_path = options["csv_file"]
        created_count = 0
        skipped_count = 0
        error_count = 0

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(
                reader, start=2
            ):  # start=2 to account for header
                try:
                    time = parse_datetime(row["time"])
                    if time is None:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Row {row_num}: Could not parse time '{row['time']}', skipping."
                            )
                        )
                        error_count += 1
                        continue

                    # Make timezone-aware if naive
                    if timezone.is_naive(time):
                        time = timezone.make_aware(time)

                    employee = random.choice(employees)

                    # Skip if an identical report already exists
                    if IncidentReport.objects.filter(
                        time=time, employee=employee
                    ).exists():
                        skipped_count += 1
                        continue

                    merchandise_cost = row["merchandise_cost"].strip() or None
                    merchandise_description = row["merchandise_description"].strip()

                    incident_report = IncidentReport.objects.create(
                        time=time,
                        summary=row["summary"].strip(),
                        merchandise_cost=merchandise_cost,
                        merchandise_description=merchandise_description,
                        employee=employee,
                        geography=employee.geography,
                    )

                    # Assign 1-4 random categories via the through model
                    selected_categories = random.sample(
                        categories, k=random.randint(1, min(4, len(categories)))
                    )
                    for category in selected_categories:
                        IncidentReportCategory.objects.create(
                            incident_report=incident_report,
                            category=category,
                            assigned_at=time,
                        )

                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Row {row_num}: Created report for {employee.given_name} {employee.surname} "
                            f"with {len(selected_categories)} categor{'y' if len(selected_categories) == 1 else 'ies'}"
                        )
                    )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Row {row_num}: Unexpected error — {e}")
                    )
                    error_count += 1
                    continue

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created: {created_count}, Skipped: {skipped_count}, Errors: {error_count}"
            )
        )
