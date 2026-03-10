from zoneinfo import ZoneInfo

from django import forms
from django.utils import timezone

from .models import IncidentReport, IncidentReportCategory


class IncidentReportCategoryInlineForm(forms.ModelForm):
    """
    Inline form for the IncidentReportCategory through model.
    assigned_at is a DateTimeField — we apply the same UTC conversion as the
    main form so category assignments are also stored in UTC.
    """

    assigned_at = forms.DateTimeField(
        label="Assigned At (your local time)",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"],
    )

    class Meta:
        model = IncidentReportCategory
        fields = ["category", "assigned_at"]

    def __init__(self, *args, **kwargs):
        self.user_tz = ZoneInfo(
            kwargs.pop("user_tz", None) or timezone.get_current_timezone_name()
        )
        super().__init__(*args, **kwargs)

    def clean_assigned_at(self):
        value = self.cleaned_data.get("assigned_at")
        if value is None:
            return value
        if timezone.is_naive(value):
            value = value.replace(tzinfo=self.user_tz, fold=0)
        return value.astimezone(ZoneInfo("UTC"))


class AdminIncidentReportForm(forms.ModelForm):
    """
    Admin form for IncidentReport.

    TIME STRATEGY:
    - The admin widget submits naive datetimes (no tzinfo).
    - clean_time() attaches the user's local timezone and converts to UTC.
    - Everything stored in the database is UTC.
    - validate_past_datetime always receives an aware datetime.
    """

    time = forms.DateTimeField(
        label="Incident Time (your local time)",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"],
        help_text="Enter the local time of the incident. It will be stored as UTC.",
    )

    class Meta:
        model = IncidentReport
        # categories is M2M via through model — handled by the inline, not this form
        # created_at / updated_at are auto-managed by Django
        exclude = ["categories"]

    def __init__(self, *args, **kwargs):
        self.user_tz = ZoneInfo(
            kwargs.pop("user_tz", None) or timezone.get_current_timezone_name()
        )
        super().__init__(*args, **kwargs)

    def clean_time(self):
        value = self.cleaned_data.get("time")
        if value is None:
            return value
        if timezone.is_naive(value):
            # Attach the user's local timezone, then convert to UTC for storage.
            # fold=0: on the ambiguous fall-back hour, take the first occurrence.
            value = value.replace(tzinfo=self.user_tz, fold=0)
        return value.astimezone(ZoneInfo("UTC"))
