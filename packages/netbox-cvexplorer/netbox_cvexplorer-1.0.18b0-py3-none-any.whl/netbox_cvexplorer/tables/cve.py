from netbox.tables import NetBoxTable
from netbox.tables.columns import ToggleColumn
from django_tables2 import Column, TemplateColumn
from netbox_cvexplorer.models import CVE

class CVETable(NetBoxTable):
    pk = ToggleColumn()
    cve_number = Column(linkify=True, verbose_name="CVE")
    title = Column()
    score = TemplateColumn(verbose_name="CVSS",
        template_code="{{ render_score|safe }}",
        orderable=True)
    status = TemplateColumn(verbose_name="Status",
        template_code='{{ render_status|safe }}',
        orderable=True)
    date_imported = Column(verbose_name="Importiert")
    date_updated = Column(verbose_name="Aktualisiert")

    class Meta:
        model = CVE
        fields = ("pk","cve_number","title","score","status","date_imported","date_updated")
        default_columns = ("cve_number","title","score","status","date_updated")
        order_by = ("-date_updated",)
        empty_text = "Keine CVEs gefunden."

    def render_score(self, value):
        try:
            s = float(value or 0)
        except (TypeError, ValueError):
            s = 0.0
        if s >= 9:
            cls = "bg-danger"
        elif s >= 7:
            cls = "bg-warning text-dark"
        elif s >= 4:
            cls = "bg-info"
        else:
            cls = "bg-success"
        return format_html('<span class="badge {}">{:.1f}</span>', cls, s)

    def render_status(self, value):
        if value == 1:
            return format_html('<span class="badge bg-success">Erledigt</span>')
        return format_html('<span class="badge bg-warning text-dark">Offen</span>')