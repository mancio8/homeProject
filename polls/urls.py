from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('preferiti/', views.aggiungi_preferito, name='aggiungi_preferito'),
    path('calendar/', views.calendario, name='calendar'),
    path('classifica/', views.table_view, name='table_view'),
]