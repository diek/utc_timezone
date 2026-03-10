from django.contrib import admin

from .forms import AdminIncidentReportForm, IncidentReportCategoryInlineForm
from .models import IncidentCategory, IncidentReport, IncidentReportCategory


@admin.register(IncidentCategory)
class IncidentCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "notes", "search_terms")
    search_fields = ("category",)


class IncidentReportCategoryInline(admin.TabularInline):
    form = IncidentReportCategoryInlineForm
    model = IncidentReportCategory
    extra = 1
    fields = ["category", "assigned_at"]
    min_num = 1  # Enforces at least one category in the inline


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    form = AdminIncidentReportForm
    list_display = (
        "id",
        "geography",
        "employee",
        "time",
        "summary",
        "merchandise_cost",
        "merchandise_description",
    )
    list_filter = ("time",)
    search_fields = ("summary", "merchandise_description")
    raw_id_fields = ("employee",)
    inlines = [IncidentReportCategoryInline]


@admin.register(IncidentReportCategory)
class IncidentReportCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "incident_report", "category", "assigned_at")
    list_filter = ("assigned_at",)
    raw_id_fields = ("incident_report", "category")
