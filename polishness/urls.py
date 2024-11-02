from __future__ import annotations

from django.urls import path

from . import views

app_name = "polishness"

urlpatterns = [
    path("", views.home, name="home"),
    path("contact/", views.contact, name="contact"),
    path("monuments/", views.monuments, name="monuments"),
    path("trips/", views.trips, name="trips"),
    path("monument/<int:pk>/", views.monument_single, name="monument_single"),
    path("monument/archeo/<int:pk>/", views.monument_single_archeo, name="monument_single_archeo"),
    path("monument/<int:pk>/ai/", views.monument_single_ai, name="monument_single_ai"),
    path("monument/<int:pk>/photos/", views.monument_single_photos, name="monument_single_photos"),
    path("monument/archeo/<int:pk>/ai/", views.monument_archeo_single_ai, name="monument_archeo_single_ai"),
    path("poland-in-numbers/", views.poland_in_numbers, name="poland_in_numbers"),
    path(
        "poland-in-numbers/<int:field_id>/<str:field_name>/",
        views.poland_in_numbers_fields,
        name="poland_in_numbers_fields",
    ),
    path(
        "poland-in-numbers/<int:field_id>/<int:field_variable_id>/<str:field_variable_name>/",
        views.poland_in_numbers_field_browser,
        name="poland_in_numbers_field_browser",
    ),
    path("nature/", views.nature, name="nature"),
    path("nature/<int:pk>/", views.nature_single, name="nature_single"),
    path("nature/<int:pk>/ai/", views.nature_single_ai, name="nature_single_ai"),
    path("photo_discovery/", views.photo_discovery, name="photo_discovery"),
    path("history/", views.history, name="history"),
]
