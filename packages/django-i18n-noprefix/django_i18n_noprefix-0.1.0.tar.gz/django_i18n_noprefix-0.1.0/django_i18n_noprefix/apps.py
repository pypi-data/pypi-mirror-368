"""
Django app configuration for django-i18n-noprefix.
"""

from django.apps import AppConfig
from django.core.checks import Error, Warning, register
from django.utils.translation import gettext_lazy as _


class I18nNoPrefixConfig(AppConfig):
    """Configuration for django-i18n-noprefix app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_i18n_noprefix"
    verbose_name = _("Django i18n No-Prefix")

    def ready(self):
        """
        Perform initialization when the app is ready.

        This method is called once Django has loaded all apps.
        We use it to register our system checks.
        """
        # Register system checks
        register(check_middleware_configuration, "django_i18n_noprefix")
        register(check_language_configuration, "django_i18n_noprefix")
        register(check_url_configuration, "django_i18n_noprefix")


def check_middleware_configuration(app_configs, **kwargs):
    """
    Check that the middleware is properly configured.

    This ensures that:
    1. Our middleware is installed
    2. Django's LocaleMiddleware is not installed (would conflict)
    3. SessionMiddleware comes before our middleware (if used)
    """
    from django.conf import settings

    errors = []

    middleware = getattr(settings, "MIDDLEWARE", [])

    # Check if our middleware is installed
    our_middleware = "django_i18n_noprefix.middleware.NoPrefixLocaleMiddleware"
    if our_middleware not in middleware:
        errors.append(
            Warning(
                "django_i18n_noprefix.middleware.NoPrefixLocaleMiddleware not found in MIDDLEWARE",
                hint='Add "django_i18n_noprefix.middleware.NoPrefixLocaleMiddleware" to your MIDDLEWARE setting.',
                id="django_i18n_noprefix.W001",
            )
        )

    # Check for conflicting middleware
    django_locale_middleware = "django.middleware.locale.LocaleMiddleware"
    if django_locale_middleware in middleware:
        errors.append(
            Error(
                "Both LocaleMiddleware and NoPrefixLocaleMiddleware are installed",
                hint='Remove "django.middleware.locale.LocaleMiddleware" from MIDDLEWARE. '
                "NoPrefixLocaleMiddleware replaces it.",
                id="django_i18n_noprefix.E001",
            )
        )

    # Check middleware ordering
    if our_middleware in middleware:
        our_index = middleware.index(our_middleware)

        # SessionMiddleware should come before our middleware
        session_middleware = "django.contrib.sessions.middleware.SessionMiddleware"
        if session_middleware in middleware:
            session_index = middleware.index(session_middleware)
            if session_index > our_index:
                errors.append(
                    Warning(
                        "SessionMiddleware should come before NoPrefixLocaleMiddleware",
                        hint="Move SessionMiddleware before NoPrefixLocaleMiddleware in MIDDLEWARE.",
                        id="django_i18n_noprefix.W002",
                    )
                )

        # CommonMiddleware should come before our middleware
        common_middleware = "django.middleware.common.CommonMiddleware"
        if common_middleware in middleware:
            common_index = middleware.index(common_middleware)
            if common_index > our_index:
                errors.append(
                    Warning(
                        "CommonMiddleware should come before NoPrefixLocaleMiddleware",
                        hint="Move CommonMiddleware before NoPrefixLocaleMiddleware in MIDDLEWARE.",
                        id="django_i18n_noprefix.W003",
                    )
                )

    return errors


def check_language_configuration(app_configs, **kwargs):
    """
    Check that language settings are properly configured.

    This ensures that:
    1. USE_I18N is True
    2. LANGUAGES is defined and not empty
    3. LANGUAGE_CODE is in LANGUAGES
    """
    from django.conf import settings

    errors = []

    # Check USE_I18N
    if not getattr(settings, "USE_I18N", False):
        errors.append(
            Error(
                "USE_I18N is not enabled",
                hint="Set USE_I18N = True in your settings.",
                id="django_i18n_noprefix.E002",
            )
        )

    # Check LANGUAGES
    languages = getattr(settings, "LANGUAGES", [])
    if not languages:
        errors.append(
            Error(
                "LANGUAGES setting is empty or not defined",
                hint="Define LANGUAGES in your settings with at least one language.",
                id="django_i18n_noprefix.E003",
            )
        )
    else:
        # Check LANGUAGE_CODE is in LANGUAGES
        language_code = getattr(settings, "LANGUAGE_CODE", "en-us")
        language_codes = [lang[0] for lang in languages]
        if language_code not in language_codes:
            errors.append(
                Warning(
                    f'LANGUAGE_CODE "{language_code}" is not in LANGUAGES',
                    hint=f'Add "{language_code}" to LANGUAGES or change LANGUAGE_CODE to one of: {", ".join(language_codes)}',
                    id="django_i18n_noprefix.W004",
                )
            )

    # Check for i18n_patterns in ROOT_URLCONF (would add prefixes)
    try:
        # This is a simple check - just warn if i18n_patterns is imported
        # A more thorough check would require parsing the URL configuration
        import importlib

        root_urlconf = getattr(settings, "ROOT_URLCONF", None)
        if root_urlconf:
            try:
                url_module = importlib.import_module(root_urlconf)
                module_source = str(url_module.__file__)
                if module_source:
                    import os

                    if os.path.exists(module_source):
                        with open(module_source) as f:
                            content = f.read()
                            if "i18n_patterns" in content:
                                errors.append(
                                    Warning(
                                        "i18n_patterns detected in ROOT_URLCONF",
                                        hint="Remove i18n_patterns from your URL configuration. "
                                        "django-i18n-noprefix handles i18n without URL prefixes.",
                                        id="django_i18n_noprefix.W005",
                                    )
                                )
            except (OSError, ImportError, AttributeError):
                # Ignore errors in checking - this is just a helpful warning
                pass
    except ImportError:
        # Django URLs not available, skip this check
        pass

    return errors


def check_url_configuration(app_configs, **kwargs):
    """
    Check that URLs are properly configured for language switching.

    This is an optional check - the package works without these URLs,
    but they're needed for the language switching views.
    """
    from django.conf import settings
    from django.urls import NoReverseMatch, reverse

    errors = []

    # Try to reverse our URLs to see if they're included
    try:
        reverse("django_i18n_noprefix:change_language", args=["en"])
    except NoReverseMatch:
        # Only warn if our app is installed
        if "django_i18n_noprefix" in settings.INSTALLED_APPS:
            errors.append(
                Warning(
                    "django_i18n_noprefix URLs are not included",
                    hint="Add \"path('i18n/', include('django_i18n_noprefix.urls'))\" to your URL configuration "
                    "to enable language switching views.",
                    id="django_i18n_noprefix.W006",
                )
            )

    return errors
