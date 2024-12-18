from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('preferiti/', views.aggiungi_preferito, name='aggiungi_preferito'),
    path('calendar/', views.calendario, name='calendar'),
    path('table/', views.table_view, name='table_view'),
    path('ferie/', views.riepilogo_ferie_permessi, name='riepilogo'),  # Definisci qui l'URL
    path('reset_ferie_permessi/', views.reset_ferie_permessi, name='reset_ferie_permessi'),
]