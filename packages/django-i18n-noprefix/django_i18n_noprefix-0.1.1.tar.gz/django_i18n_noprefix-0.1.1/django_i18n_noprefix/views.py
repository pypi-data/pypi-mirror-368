"""
Views for django-i18n-noprefix.
"""

import json

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from .utils import activate_language, is_valid_language


@never_cache
@require_http_methods(["GET", "POST"])
def change_language(request: HttpRequest, lang_code: str) -> HttpResponse:
    """
    Change the language for the current user.

    This view changes the user's language preference and redirects
    them back to the previous page or a specified next URL.

    Args:
        request: The HTTP request object
        lang_code: The language code to switch to

    Returns:
        HttpResponse redirect to the previous page or next URL

    Example URLs:
        /i18n/set-language/ko/
        /i18n/set-language/en/?next=/about/
    """
    # Validate language code
    if not is_valid_language(lang_code):
        # Invalid language, redirect to referrer or home
        next_url = get_next_url(request)
        return redirect(next_url)

    # Activate the language
    activate_language(request, lang_code)

    # Get the next URL
    next_url = get_next_url(request)

    # Redirect to the next URL
    response = redirect(next_url)

    # Save language to cookie (session will be saved by activate_language)
    response.set_cookie(
        key=settings.LANGUAGE_COOKIE_NAME,
        value=lang_code,
        max_age=(
            settings.LANGUAGE_COOKIE_AGE
            if hasattr(settings, "LANGUAGE_COOKIE_AGE")
            else 365 * 24 * 60 * 60
        ),
        path=(
            settings.LANGUAGE_COOKIE_PATH
            if hasattr(settings, "LANGUAGE_COOKIE_PATH")
            else "/"
        ),
        domain=(
            settings.LANGUAGE_COOKIE_DOMAIN
            if hasattr(settings, "LANGUAGE_COOKIE_DOMAIN")
            else None
        ),
        secure=(
            settings.LANGUAGE_COOKIE_SECURE
            if hasattr(settings, "LANGUAGE_COOKIE_SECURE")
            else False
        ),
        httponly=(
            settings.LANGUAGE_COOKIE_HTTPONLY
            if hasattr(settings, "LANGUAGE_COOKIE_HTTPONLY")
            else False
        ),
        samesite=(
            settings.LANGUAGE_COOKIE_SAMESITE
            if hasattr(settings, "LANGUAGE_COOKIE_SAMESITE")
            else "Lax"
        ),
    )

    return response


@never_cache
@require_POST
def set_language_ajax(request: HttpRequest) -> JsonResponse:
    """
    AJAX endpoint for changing language.

    Expects JSON POST data with 'language' field.

    Args:
        request: The HTTP request object

    Returns:
        JsonResponse with success status and redirect URL

    Example:
        POST /i18n/set-language-ajax/
        Content-Type: application/json
        {"language": "ko", "next": "/about/"}
    """
    try:
        # Parse JSON data
        data = json.loads(request.body)
        lang_code = data.get("language")

        if not lang_code:
            return JsonResponse(
                {"success": False, "error": "No language specified"}, status=400
            )

        # Validate language code
        if not is_valid_language(lang_code):
            return JsonResponse(
                {"success": False, "error": f"Invalid language code: {lang_code}"},
                status=400,
            )

        # Activate the language
        activate_language(request, lang_code)

        # Get the next URL
        next_url = data.get("next") or get_next_url(request)

        # Return success response
        # The middleware will handle saving to session/cookie
        return JsonResponse(
            {"success": True, "language": lang_code, "redirect": next_url}
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON data"}, status=400
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def get_next_url(request: HttpRequest, default: str = "/") -> str:
    """
    Get the next URL to redirect to after language change.

    Priority:
    1. 'next' parameter in GET/POST
    2. HTTP_REFERER header
    3. Default URL (/)

    Args:
        request: The HTTP request object
        default: Default URL if no next URL is found

    Returns:
        The URL to redirect to
    """
    # Check GET parameter
    next_url = request.GET.get("next")

    # Check POST parameter
    if not next_url and request.method == "POST":
        next_url = request.POST.get("next")

    # Check referrer
    if not next_url:
        next_url = request.META.get("HTTP_REFERER")

    # Validate and sanitize the URL
    if next_url:
        # Basic validation - ensure it's a relative URL or same domain
        # This prevents open redirect vulnerabilities
        if is_safe_url(next_url, request):
            return next_url

    return default


def is_safe_url(url: str, request: HttpRequest) -> bool:
    """
    Check if a URL is safe for redirection.

    A URL is considered safe if it's:
    - A relative URL (starts with /)
    - On the same domain as the request

    Args:
        url: The URL to check
        request: The HTTP request object

    Returns:
        True if the URL is safe, False otherwise
    """
    if not url:
        return False

    # Allow relative URLs
    if url.startswith("/"):
        return True

    # For absolute URLs, check if they're on the same domain
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)
        request_host = request.get_host()

        # Check if the domain matches
        if parsed.netloc == request_host:
            return True

        # Also allow if no domain is specified (relative URL)
        if not parsed.netloc:
            return True

    except Exception:
        pass

    return False
