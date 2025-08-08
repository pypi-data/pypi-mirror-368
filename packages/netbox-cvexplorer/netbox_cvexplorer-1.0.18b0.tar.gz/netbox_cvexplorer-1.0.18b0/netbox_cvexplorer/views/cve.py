from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
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
    paginate_by = 25   # <- hinzufügen

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(cve_number__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #table = CVETable(self.object_list)
        #RequestConfig(self.request, paginate={"per_page": 25}).configure(table)
        #context['table'] = table
        context['search_query'] = self.request.GET.get("q", "")
        return context

class CVEDetailView(DetailView):
    model = CVE
    template_name = 'netbox_cvexplorer/cve_detail.html'
    context_object_name = 'cve'

class CVECreateView(PermissionRequiredMixin, CreateView):
    model = CVE
    form_class = CVEForm
    template_name = 'netbox_cvexplorer/cve_form.html'
    success_url = reverse_lazy('plugins:netbox_cvexplorer:cve_list')
    permission_required = 'netbox_cvexplorer.add_cve'

    def form_valid(self, form):
        obj = form.save(commit=False)
        # optional: weitere Felder 
        obj.save()
        messages.success(self.request, f"CVE wurde angelegt: {obj.cve_number}")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, f"CVE Eintrag ungültig: {form.errors.as_text()}")
        return super().form_invalid(form)

class CVEUpdateView(PermissionRequiredMixin, UpdateView):
    model = CVE
    form_class = CVEForm
    template_name = 'netbox_cvexplorer/cve_form.html'
    permission_required = 'netbox_cvexplorer.change_cve'

    def get_success_url(self):
        obj = form.save(commit=False)
        # optional: weitere Felder 
        obj.save()
        messages.success(self.request, f"CVE wurde aktualisiert: {self.object.cve_number}")
        return reverse_lazy('plugins:netbox_cvexplorer:cve_detail', args=[self.object.pk])

class CVEDeleteView(PermissionRequiredMixin, DeleteView):
    model = CVE
    template_name = 'generic/confirm_delete.html'  # NetBox hat oft sowas schon
    permission_required = 'netbox_cvexplorer.delete_cve'
    success_url = reverse_lazy('plugins:netbox_cvexplorer:cve_list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"{obj.cve_number} wurde gelöscht.")
        return super().delete(request, *args, **kwargs)