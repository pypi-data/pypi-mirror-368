"""
Django i18n middleware without URL prefixes.

This middleware provides internationalization support without adding
language prefixes to URLs (e.g., /en/, /ko/, /ja/).
"""

import logging
from typing import Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils import translation
from django.utils.translation import get_language_from_request

logger = logging.getLogger(__name__)


class NoPrefixLocaleMiddleware:
    """
    Middleware for handling i18n without URL prefixes.

    Language detection priority:
    1. Session (django_language key)
    2. Cookie (django_language or custom)
    3. Accept-Language header
    4. Default language (LANGUAGE_CODE setting)
    """

    def __init__(self, get_response):
        """Initialize the middleware."""
        self.get_response = get_response

        # Get custom settings or use defaults
        self.cookie_name = getattr(
            settings, "I18N_NOPREFIX_COOKIE_NAME", settings.LANGUAGE_COOKIE_NAME
        )
        self.cookie_age = getattr(
            settings,
            "I18N_NOPREFIX_COOKIE_AGE",
            settings.LANGUAGE_COOKIE_AGE or 365 * 24 * 60 * 60,  # 1 year
        )
        self.cookie_path = getattr(
            settings, "I18N_NOPREFIX_COOKIE_PATH", settings.LANGUAGE_COOKIE_PATH
        )
        self.cookie_domain = getattr(
            settings, "I18N_NOPREFIX_COOKIE_DOMAIN", settings.LANGUAGE_COOKIE_DOMAIN
        )
        self.cookie_secure = getattr(
            settings,
            "I18N_NOPREFIX_COOKIE_SECURE",
            settings.LANGUAGE_COOKIE_SECURE or False,
        )
        self.cookie_httponly = getattr(
            settings,
            "I18N_NOPREFIX_COOKIE_HTTPONLY",
            settings.LANGUAGE_COOKIE_HTTPONLY or False,
        )
        self.cookie_samesite = getattr(
            settings,
            "I18N_NOPREFIX_COOKIE_SAMESITE",
            settings.LANGUAGE_COOKIE_SAMESITE or "Lax",
        )

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request and response."""
        # Get the current language
        language = self.get_language(request)

        # Activate the language
        translation.activate(language)
        request.LANGUAGE_CODE = language

        # Process the view
        response = self.get_response(request)

        # Save language preference if it changed
        # Use request.LANGUAGE_CODE which may have been updated by views
        self.save_language(request, response, request.LANGUAGE_CODE)

        return response

    def get_language(self, request: HttpRequest) -> str:
        """
        Determine the language for the request.

        Priority:
        1. Session (django_language)
        2. Cookie
        3. Accept-Language header
        4. Default language
        """
        # 1. Check session
        language = self.get_language_from_session(request)
        if language:
            return language

        # 2. Check cookie
        language = self.get_language_from_cookie(request)
        if language:
            return language

        # 3. Check Accept-Language header
        language = self.get_language_from_header(request)
        if language:
            return language

        # 4. Return default language
        return settings.LANGUAGE_CODE

    def get_language_from_session(self, request: HttpRequest) -> Optional[str]:
        """Get language from session if available."""
        if hasattr(request, "session") and "django_language" in request.session:
            language = request.session["django_language"]
            if self.is_valid_language(language):
                return language
        return None

    def get_language_from_cookie(self, request: HttpRequest) -> Optional[str]:
        """Get language from cookie if available."""
        language = request.COOKIES.get(self.cookie_name)
        if language and self.is_valid_language(language):
            return language
        return None

    def get_language_from_header(self, request: HttpRequest) -> Optional[str]:
        """
        Get language from Accept-Language header.
        Uses Django's built-in language detection.
        """
        # Use Django's built-in function to parse Accept-Language header
        language = get_language_from_request(request, check_path=False)
        if language and self.is_valid_language(language):
            return language
        return None

    def is_valid_language(self, language: str) -> bool:
        """Check if the language code is valid."""
        available_languages = [lang[0] for lang in settings.LANGUAGES]
        return language in available_languages

    def save_language(
        self, request: HttpRequest, response: HttpResponse, current_language: str
    ) -> None:
        """
        Save language preference if it changed.

        - Saves to session if available
        - Always saves to cookie for session-less users
        """
        # Check if language was explicitly set (e.g., via set_language view)
        language_was_set = getattr(request, "_language_was_set", False)

        # Save if language was explicitly set or if there's no cookie yet
        should_save = language_was_set or not request.COOKIES.get(self.cookie_name)

        if should_save:
            # Save to session if available
            if (
                hasattr(request, "session")
                and hasattr(request.session, "session_key")
                and request.session.session_key
            ):
                request.session["django_language"] = current_language
            elif hasattr(request, "session") and not hasattr(
                request.session, "session_key"
            ):
                # For dict-like sessions (e.g., in tests)
                request.session["django_language"] = current_language

            # Always save to cookie
            response.set_cookie(
                key=self.cookie_name,
                value=current_language,
                max_age=self.cookie_age,
                path=self.cookie_path,
                domain=self.cookie_domain,
                secure=self.cookie_secure,
                httponly=self.cookie_httponly,
                samesite=self.cookie_samesite,
            )
