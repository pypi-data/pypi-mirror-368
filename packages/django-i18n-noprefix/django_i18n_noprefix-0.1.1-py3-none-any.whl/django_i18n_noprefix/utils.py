"""
Utility functions for django-i18n-noprefix.

This module provides minimal helper functions that complement Django's i18n.
Most i18n functionality should use Django's built-in functions directly:
- Use `translation.get_language()` instead of a custom wrapper
- Use `settings.LANGUAGES` directly for available languages
- Use `translation.get_language_info()` for language names
"""

from django.conf import settings
from django.http import HttpRequest
from django.utils import translation


def activate_language(request: HttpRequest, lang_code: str) -> bool:
    """
    Activate a language for the current request.

    This is a convenience function to use in views when you need to
    change the language programmatically. It combines Django's
    translation.activate() with request attribute setting.

    Args:
        request: The HTTP request object
        lang_code: The language code to activate

    Returns:
        True if the language was activated, False if invalid

    Example:
        >>> activate_language(request, 'ko')
        True
    """
    if is_valid_language(lang_code):
        translation.activate(lang_code)
        request.LANGUAGE_CODE = lang_code
        request._language_was_set = True  # Flag for middleware to save cookie

        # Save to session if available
        if hasattr(request, "session"):
            request.session["django_language"] = lang_code

        return True
    return False


def is_valid_language(lang_code: str) -> bool:
    """
    Check if a language code is valid (exists in LANGUAGES setting).

    Args:
        lang_code: The language code to validate

    Returns:
        True if the language code is valid, False otherwise

    Example:
        >>> is_valid_language('ko')
        True
        >>> is_valid_language('invalid')
        False
    """
    available_languages = [lang[0] for lang in settings.LANGUAGES]
    return lang_code in available_languages
