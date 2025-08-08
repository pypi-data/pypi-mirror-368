from django.urls import path
from .views import CVEListView, CVECreateView

urlpatterns = [
    path('cve/', CVEListView.as_view(), name='cve_list'),
    path('cves/add/', CVECreateView.as_view(), name='cve_add'),
    path('cves/<int:pk>/', CVEDetailView.as_view(), name='cve_detail'), 
    path('cves/<int:pk>/edit/', CVEUpdateView.as_view(), name='cve_edit'),
    path('cves/<int:pk>/delete/', CVEDeleteView.as_view(), name='cve_delete'),
]