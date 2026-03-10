from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from .validators import validate_past_datetime
from employees.models import Employee, Geographical


class IncidentCategory(models.Model):
    category = models.CharField(max_length=122, unique=True)
    notes = models.TextField(null=True, blank=True)
    search_terms = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )

    def __str__(self):
        return self.category

    class Meta:
        ordering = ["category"]
        verbose_name_plural = "Incident Categories"


class IncidentReport(Geographical, models.Model):
    employee = models.ForeignKey(Employee, models.PROTECT)
    time = models.DateTimeField(db_index=True, validators=[validate_past_datetime])
    summary = models.TextField()
    merchandise_cost = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True
    )
    merchandise_description = models.TextField(blank=True)

    categories = models.ManyToManyField(
        IncidentCategory,
        through="IncidentReportCategory",
        related_name="incident_report_categories",
    )

    class Meta:
        verbose_name_plural = "Incident Reports"

    def __str__(self):
        return f"{self.summary}, {self.time}"

    # NOTE: The categories validation has been intentionally moved to the admin
    # inline (min_num=1 on IncidentReportCategoryInline). It cannot live here
    # because M2M through-model rows are saved AFTER the parent model's
    # full_clean(), so categories.count() is always 0 at validation time for
    # new records, and Django cannot map a 'categories' ValidationError back to
    # the admin form because the field is excluded.


class IncidentReportCategory(models.Model):
    incident_report = models.ForeignKey(
        "IncidentReport",
        on_delete=models.CASCADE,
        related_name="incident_categories",
        db_index=True,
    )
    category = models.ForeignKey(
        "IncidentCategory",
        on_delete=models.CASCADE,
        related_name="incident_reports",
        db_index=True,
    )
    assigned_at = models.DateTimeField(db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("incident_report", "category"),
                name="unique_incident_category",
            )
        ]
        ordering = ("-assigned_at",)
        verbose_name = "Incident Report Category"
        verbose_name_plural = "Incident Report and Categories"

    def __str__(self):
        return f"IncidentReportCategory #{self.pk}"

    def category_name(self):
        return self.category.category

    def assigned_date_short(self):
        return self.assigned_at.strftime("%b %d, %Y")

    def assigned_date_long(self):
        return self.assigned_at.strftime("%B %d, %Y at %I:%M %p")
