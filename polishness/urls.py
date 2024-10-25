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
    path("history/", views.history, name="history"),
]
