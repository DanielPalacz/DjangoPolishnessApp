from django.urls import path
from . import views

app_name = 'polishness'

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('monuments/', views.monuments, name='monuments'),
    path('trips/', views.trips, name='trips'),
    path('<int:pk>/', views.monument_single, name='monument_single'),
    path('<int:pk>/ai/', views.monument_single_ai, name='monument_single_ai'),
    path('poland-in-numbers/', views.poland_in_numbers, name='poland_in_numbers'),
    path('history/', views.history, name='history'),
]