from django.urls import path

from . import views
from . import bilancio_views

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
    path('libri/delete/<int:book_id>/', views.delete_book, name='delete_book'),
    path('libri/import/', views.import_books, name='import_books'),
    path('libri/download/', views.download_books_json, name='download_books_json'),
    path('bilancio/<int:anno>/', bilancio_views.bilancio_annuale, name="bilancio_annuale"),
    path('bilancio/evento/<str:evento>/', bilancio_views.bilancio_evento, name="bilancio_evento"),
    path('bilancio/<int:anno>/scarica/', bilancio_views.scarica_pdf, name="scarica_pdf"),
    path('bilancio/gestione/', bilancio_views.gestione_bilancio, name="gestione_bilancio"),
    path("bilancio/<int:anno>/download_csv/", bilancio_views.scarica_bilancio_csv, name="scarica_bilancio_csv"),
    path('bilancio/evento/<str:evento>/scarica-bilancio-csv/', bilancio_views.scarica_bilancio_evento_csv, name='scarica_bilancio_evento_csv'),
    
]