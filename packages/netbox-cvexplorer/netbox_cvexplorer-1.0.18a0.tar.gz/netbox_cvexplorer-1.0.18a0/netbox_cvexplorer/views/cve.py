from django.views.generic import ListView, CreateView
from django_tables2 import RequestConfig
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from netbox_cvexplorer.models import CVE
from netbox_cvexplorer.tables import CVETable
from netbox_cvexplorer.forms import CVEForm

class CVEListView(ListView):
    model = CVE
    template_name = 'netbox_cvexplorer/cve_list.html'
    context_object_name = 'cve_list'

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(cve_number__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = CVETable(self.object_list)
        RequestConfig(self.request, paginate={"per_page": 25}).configure(table)
        context['table'] = table
        context['search_query'] = self.request.GET.get("q", "")
        return context


class CVECreateView(PermissionRequiredMixin, CreateView):
    model = CVE
    form_class = CVEForm
    template_name = 'netbox_cvexplorer/cve_form.html'
    success_url = reverse_lazy('plugins:netbox_cvexplorer:cve_list')
    permission_required = 'netbox_cvexplorer.add_cve'

    def form_valid(self, form):
        messages.success(self.request, "CVE wurde angelegt.")
        return super().form_valid(form)
