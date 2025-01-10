from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('preferiti/', views.aggiungi_preferito, name='aggiungi_preferito'),
    path('calendar/', views.calendario, name='calendar'),
    path('classifica/', views.table_view, name='table_view'),
    path('table/', views.table_view, name='table_view'),
    path('ferie/', views.riepilogo_ferie_permessi, name='riepilogo'),  # Definisci qui l'URL
    path('reset_ferie_permessi/', views.reset_ferie_permessi, name='reset_ferie_permessi'),
    path('esporta_pdf/', views.esporta_pdf, name='esporta_pdf'),
    path('artisti/', views.artist_songs_view, name='artist_songs'),
    path('libri/', views.add_and_view_books, name='view_books'),
    path('delete/<str:title>/', views.delete_book, name='delete_book'),
    path('download_books_json/', views.download_books_json, name='download_books_json'),
]