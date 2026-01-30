from django.urls import path
from . import views

urlpatterns = [
    path("importa/", views.importa_json, name="importa_json"),
    path("importa/success/", views.import_success, name="import_success"),
    path("statistiche/multi/", views.statistiche_squadra_multi, name="statistiche_multi"),
    path("statistiche/<int:stagione_id>/", views.statistiche_squadra, name="statistiche"),

]
