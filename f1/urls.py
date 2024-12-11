from django.urls import path
from . import views

urlpatterns = [
    path('next-race/', views.get_next_race, name='next_race'),
    path('last-race-results/', views.get_last_race_results, name='last_race_results'),
    path('driver-standings/', views.get_driver_standings, name='driver_standings'),
    path('constructor-standings/', views.get_constructor_standings, name='constructor_standings'),
    path('drivers/', views.get_all_drivers, name='drivers_card'),
    path('constructors/', views.get_all_constructors, name='constructors_card'),
    path('home/', views.home, name='homef1'),
    
    # Altre rotte per gli altri metodi
]
