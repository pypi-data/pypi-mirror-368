"""
Template tags for django-i18n-noprefix.

These tags complement Django's built-in i18n template tags.
Use Django's tags for most i18n operations:
- {% get_current_language %} for current language code
- {% get_available_languages %} for available languages
- {% get_language_info %} for language details

Our tags focus on language switching functionality.
"""

from django import template
from django.urls import reverse
from django.utils import translation
from django.utils.http import urlencode

from ..utils import is_valid_language

register = template.Library()


@register.simple_tag(takes_context=True)
def switch_language_url(context, lang_code, next_url=None):
    """
    Generate URL for switching to a specific language.

    Args:
        context: Template context
        lang_code: The language code to switch to
        next_url: Optional URL to redirect to after switching (default: current page)

    Returns:
        URL string for language switching

    Example:
        {% switch_language_url 'ko' %}
        {% switch_language_url 'en' next_url='/about/' %}
    """
    if not is_valid_language(lang_code):
        return "#"  # Return anchor for invalid language

    base_url = reverse("django_i18n_noprefix:change_language", args=[lang_code])

    # If no next_url provided, use the current page
    if not next_url:
        request = context.get("request")
        if request:
            next_url = request.path

    if next_url:
        params = urlencode({"next": next_url})
        return f"{base_url}?{params}"

    return base_url


@register.filter
def is_current_language(lang_code):
    """
    Check if the given language code is the current active language.

    Useful for adding CSS classes to active language links.

    Args:
        lang_code: The language code to check

    Returns:
        True if lang_code matches current language, False otherwise

    Example:
        <li class="{% if 'ko'|is_current_language %}active{% endif %}">
    """
    return lang_code == translation.get_language()


@register.simple_tag(takes_context=True)
def language_selector(context, style="dropdown", next_url=None):
    """
    Render a language selector widget.

    Args:
        context: Template context (automatic)
        style: Widget style - 'dropdown', 'list', or 'inline' (default: 'dropdown')
        next_url: URL to redirect to after language change (default: current page)

    Returns:
        Rendered language selector HTML

    Example:
        {% language_selector %}
        {% language_selector style='list' %}
        {% language_selector style='inline' next_url='/dashboard/' %}
    """
    from django.conf import settings
    from django.template.loader import render_to_string

    current_language = translation.get_language()

    # Get language info for all available languages
    languages = []
    for code, name in settings.LANGUAGES:
        languages.append(
            {
                "code": code,
                "name": name,
                "is_current": code == current_language,
                "switch_url": switch_language_url(code, next_url),
            }
        )

    # Get template based on style
    template_map = {
        "dropdown": "i18n_noprefix/language_selector.html",
        "list": "i18n_noprefix/language_selector_list.html",
        "inline": "i18n_noprefix/language_selector_inline.html",
    }

    # Select the appropriate template
    template_name = template_map.get(style, template_map["dropdown"])

    # Prepare context
    template_context = {
        "languages": languages,
        "current_language": current_language,
        "current_language_name": dict(settings.LANGUAGES).get(current_language, ""),
        "style": style,
        "next_url": next_url,
        "LANGUAGE_CODE": current_language,  # For compatibility
    }

    # Render and return the template
    return render_to_string(
        template_name, template_context, request=context.get("request")
    )
