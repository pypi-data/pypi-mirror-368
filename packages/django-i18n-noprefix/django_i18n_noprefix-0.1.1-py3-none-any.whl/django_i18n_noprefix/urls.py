"""
URL patterns for django-i18n-noprefix.
"""

from django.urls import path

from . import views

app_name = "django_i18n_noprefix"

urlpatterns = [
    # Language change URLs
    path(
        "set-language/<str:lang_code>/", views.change_language, name="change_language"
    ),
    path("set-language-ajax/", views.set_language_ajax, name="set_language_ajax"),
]
