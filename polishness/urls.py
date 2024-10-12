from django.urls import path
from . import views

app_name = 'polishness'

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('monuments/', views.monuments, name='monuments'),
    path('<int:pk>/', views.monument_single, name='monument_single'),
    # path('projects/', views.projects, name='projects'),
    # path('blog/', views.blog, name='blog'),
    # path('blog/<slug:post_slug>/', views.post_single, name='post_single'),
    # path('int:pk>/', views.monument_single, name='monument_single'),
]