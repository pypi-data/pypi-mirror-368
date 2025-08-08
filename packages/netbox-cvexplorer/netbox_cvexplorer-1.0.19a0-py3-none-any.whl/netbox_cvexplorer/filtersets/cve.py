import django_filters 
from netbox.filtersets import BaseFilterSet
from django.db.models import Q

from ..models import CVE

class CVEFilterSet(BaseFilterSet):

    q = django_filters.CharFilter(method="search", label="Search")
    score__gte = django_filters.NumberFilter(field_name="score", lookup_expr="gte", label="Min. CVSS")
    score__lte = django_filters.NumberFilter(field_name="score", lookup_expr="lte", label="Max. CVSS")

    class Meta:
        model = CVE
        fields = ["status"]

    def search(self, qs, name, value):
        if not value:
            return qs
        return qs.filter(
            Q(cve_number__icontains=value) |
            Q(title__icontains=value) |
            Q(description__icontains=value)
        )