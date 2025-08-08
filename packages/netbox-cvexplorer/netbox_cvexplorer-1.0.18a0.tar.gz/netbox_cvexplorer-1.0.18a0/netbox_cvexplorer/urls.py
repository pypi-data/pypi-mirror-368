from django.urls import path
from .views import CVEListView, CVECreateView

urlpatterns = [
    path('cve/', CVEListView.as_view(), name='cve_list'),
    path('cves/add/', CVECreateView.as_view(), name='cve_add'),
]