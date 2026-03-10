from django.core.paginator import Paginator
from django.shortcuts import render

from .models import IncidentReport


def incident_report_list(request):
    queryset = (
        IncidentReport.objects.select_related("employee")
        .prefetch_related("categories")
        .order_by("-time")
    )
    paginator = Paginator(queryset, 30)
    page = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "incidents/incident_report_list.html",
        {
            "page_obj": page,
            "paginator": paginator,
        },
    )
