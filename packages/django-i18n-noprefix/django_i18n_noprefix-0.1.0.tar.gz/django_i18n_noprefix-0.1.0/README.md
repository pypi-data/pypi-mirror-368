# django-i18n-noprefix

[![Tests](https://github.com/jinto/django-i18n-noprefix/workflows/Tests/badge.svg)](https://github.com/jinto/django-i18n-noprefix/actions/workflows/test.yml)
[![Code Quality](https://github.com/jinto/django-i18n-noprefix/workflows/Code%20Quality/badge.svg)](https://github.com/jinto/django-i18n-noprefix/actions/workflows/quality.yml)
[![Release](https://github.com/jinto/django-i18n-noprefix/workflows/Release/badge.svg)](https://github.com/jinto/django-i18n-noprefix/actions/workflows/release.yml)
[![codecov](https://codecov.io/gh/jinto/django-i18n-noprefix/branch/main/graph/badge.svg)](https://codecov.io/gh/jinto/django-i18n-noprefix)
[![PyPI Version](https://img.shields.io/pypi/v/django-i18n-noprefix.svg)](https://pypi.org/project/django-i18n-noprefix/)
[![Python Support](https://img.shields.io/pypi/pyversions/django-i18n-noprefix.svg)](https://pypi.org/project/django-i18n-noprefix/)
[![Django Support](https://img.shields.io/badge/Django-4.2%20%7C%205.0%20%7C%205.1-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/jinto/django-i18n-noprefix/blob/main/LICENSE)

**Clean URLs for multilingual Django sites without language prefixes.**

Seamlessly integrate Django's i18n framework while keeping your URLs clean. No more `/en/about/` or `/ko/about/` — just `/about/` that works in any language.

## 🎯 Why django-i18n-noprefix?

Django's built-in i18n system automatically adds language codes to your URLs (`/en/`, `/ko/`, `/ja/`). While this works, it has drawbacks:

### The Problem with URL Prefixes

| Issue | With Prefixes | With django-i18n-noprefix |
|-------|--------------|---------------------------|
| **URLs** | `/en/products/`<br>`/ko/products/` | `/products/` |
| **SEO** | Duplicate content issues | Single URL per content |
| **Sharing** | Language-specific links | Universal links |
| **User Experience** | Exposes technical details | Clean, professional URLs |
| **API Routes** | `/api/v1/en/users/` 😱 | `/api/v1/users/` ✨ |

### Real-World Example

```python
# Before: Django default i18n
https://mysite.com/en/products/laptop/    # English
https://mysite.com/ko/products/laptop/    # Korean
https://mysite.com/ja/products/laptop/    # Japanese

# After: With django-i18n-noprefix
https://mysite.com/products/laptop/        # Any language!
```

## ✨ Features

- 🚫 **No URL prefixes** — Keep URLs clean and professional
- 🔄 **Full Django i18n compatibility** — Use all Django's i18n features
- 🍪 **Smart language detection** — Session, cookie, and Accept-Language header support
- 🎨 **3 language selector styles** — Dropdown, list, or inline
- 🎯 **Framework agnostic** — Bootstrap, Tailwind, or vanilla CSS
- ⚡ **Zero configuration** — Works out of the box
- 🔒 **Production ready** — 93% test coverage
- 📦 **Lightweight** — No external dependencies except Django

## 🚀 Quick Start (5 minutes)

### 1. Install

```bash
pip install django-i18n-noprefix
```

### 2. Update Settings

```python
# settings.py

INSTALLED_APPS = [
    # ...
    'django_i18n_noprefix',  # Add this
]

MIDDLEWARE = [
    # ...
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',  # Remove this
    'django_i18n_noprefix.middleware.NoPrefixLocaleMiddleware',  # Add this
    'django.middleware.common.CommonMiddleware',
    # ...
]

# Configure languages
LANGUAGES = [
    ('en', 'English'),
    ('ko', '한국어'),
    ('ja', '日本語'),
]
LANGUAGE_CODE = 'en'
```

### 3. Add URL Pattern

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # ...
    path('i18n/', include('django_i18n_noprefix.urls')),
]
```

### 4. Add Language Selector

```django
<!-- base.html -->
{% load i18n_noprefix %}

<!DOCTYPE html>
<html>
<body>
    <!-- Add anywhere in your template -->
    {% language_selector %}

    <!-- Your content -->
    {% block content %}{% endblock %}
</body>
</html>
```

**That's it!** Your site now supports multiple languages without URL prefixes.

## 📋 Detailed Installation

### Using pip

```bash
pip install django-i18n-noprefix
```

### Using uv

```bash
uv pip install django-i18n-noprefix
```

### Development Installation

```bash
git clone https://github.com/jinto/django-i18n-noprefix.git
cd django-i18n-noprefix
pip install -e ".[dev]"
```

## 🔧 Configuration

### Basic Configuration

The minimal configuration shown in Quick Start is often sufficient. Here are all available options:

```python
# settings.py

# Required: Enable Django i18n
USE_I18N = True
USE_L10N = True  # Django < 5.0
USE_TZ = True

# Language Configuration
LANGUAGES = [
    ('en', 'English'),
    ('ko', '한국어'),
    ('ja', '日本語'),
    ('zh', '中文'),
    ('es', 'Español'),
]

LANGUAGE_CODE = 'en'  # Default language

# Optional: Customize cookie name (default: 'django_language')
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 365 * 24 * 60 * 60  # 1 year
LANGUAGE_COOKIE_PATH = '/'
LANGUAGE_COOKIE_DOMAIN = None
LANGUAGE_COOKIE_SECURE = False
LANGUAGE_COOKIE_HTTPONLY = False
LANGUAGE_COOKIE_SAMESITE = 'Lax'
```

### Language Detection Priority

Languages are detected in this order:

1. **URL parameter** (when switching languages)
2. **Session** (for logged-in users)
3. **Cookie** (for anonymous users)
4. **Accept-Language header** (browser preference)
5. **LANGUAGE_CODE setting** (fallback)

## 📖 Usage Examples

### Basic Language Selector

```django
{% load i18n_noprefix %}

<!-- Dropdown style (default) -->
{% language_selector %}

<!-- List style -->
{% language_selector style='list' %}

<!-- Inline style -->
{% language_selector style='inline' %}
```

### Custom Language Selector

```django
{% load i18n i18n_noprefix %}
{% get_current_language as CURRENT_LANGUAGE %}
{% get_available_languages as LANGUAGES %}

<!-- Custom dropdown -->
<select onchange="location.href=this.value">
    {% for lang_code, lang_name in LANGUAGES %}
        <option value="{% switch_language_url lang_code %}"
                {% if lang_code == CURRENT_LANGUAGE %}selected{% endif %}>
            {{ lang_name }}
        </option>
    {% endfor %}
</select>

<!-- Custom buttons -->
<div class="language-buttons">
    {% for lang_code, lang_name in LANGUAGES %}
        <a href="{% switch_language_url lang_code %}"
           class="btn {% if lang_code|is_current_language %}active{% endif %}">
            {{ lang_code|upper }}
        </a>
    {% endfor %}
</div>
```

### Programmatic Language Change

```python
# views.py
from django.shortcuts import redirect
from django_i18n_noprefix.utils import activate_language

def my_view(request):
    # Change language programmatically
    activate_language(request, 'ko')
    return redirect('home')

# Or in class-based views
from django.views import View

class LanguagePreferenceView(View):
    def post(self, request):
        language = request.POST.get('language')
        if language:
            activate_language(request, language)
        return redirect(request.META.get('HTTP_REFERER', '/'))
```

### AJAX Language Switching

```javascript
// JavaScript
function changeLanguage(langCode) {
    fetch('/i18n/set-language-ajax/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({language: langCode})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}
```

### Using with Django Forms

```python
# forms.py
from django import forms
from django.conf import settings

class LanguageForm(forms.Form):
    language = forms.ChoiceField(
        choices=settings.LANGUAGES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

# views.py
from django.shortcuts import redirect
from django_i18n_noprefix.utils import activate_language

def change_language_view(request):
    if request.method == 'POST':
        form = LanguageForm(request.POST)
        if form.is_valid():
            activate_language(request, form.cleaned_data['language'])
            return redirect('home')
    else:
        form = LanguageForm()
    return render(request, 'change_language.html', {'form': form})
```

## 🔄 Integration with Django i18n

This package **complements** Django's i18n system. You can use all Django i18n features:

### Using Django's Translation Features

```django
{% load i18n %}

<!-- Translation tags work normally -->
{% trans "Welcome" %}
{% blocktrans %}Hello {{ name }}{% endblocktrans %}

<!-- Get current language -->
{% get_current_language as LANGUAGE_CODE %}
Current language: {{ LANGUAGE_CODE }}

<!-- Get available languages -->
{% get_available_languages as LANGUAGES %}
```

### In Python Code

```python
from django.utils.translation import gettext as _
from django.utils.translation import get_language

def my_view(request):
    # Django's translation functions work normally
    message = _("Welcome to our site")
    current_language = get_language()

    return render(request, 'template.html', {
        'message': message,
        'language': current_language
    })
```

### Migration from Standard Django i18n

Migrating from Django's default i18n is straightforward:

1. **Remove URL prefixes**:
   ```python
   # Old: urls.py
   from django.conf.urls.i18n import i18n_patterns

   urlpatterns = i18n_patterns(
       path('about/', views.about),
       # ...
   )

   # New: urls.py
   urlpatterns = [
       path('about/', views.about),
       # ...
   ]
   ```

2. **Replace middleware** (as shown in Quick Start)

3. **Update language switcher** (use our template tags)

That's it! All your translations and language files remain unchanged.

## 🎨 Styling Options

### Bootstrap 5

```django
{% load static %}
<link href="{% static 'i18n_noprefix/css/bootstrap5.css' %}" rel="stylesheet">

{% language_selector style='dropdown' %}
```

### Tailwind CSS

```django
{% load static %}
<link href="{% static 'i18n_noprefix/css/tailwind.css' %}" rel="stylesheet">

{% language_selector style='inline' %}
```

### Vanilla CSS

```django
{% load static %}
<link href="{% static 'i18n_noprefix/css/vanilla.css' %}" rel="stylesheet">

{% language_selector style='list' %}
```

### Custom Styling

```css
/* Override CSS variables */
:root {
    --i18n-primary: #007bff;
    --i18n-primary-hover: #0056b3;
    --i18n-text: #333;
    --i18n-bg: #fff;
    --i18n-border: #ddd;
    --i18n-radius: 4px;
}

/* Or write custom CSS */
.language-selector-dropdown {
    /* Your styles */
}
```

## 📊 Django/Python Compatibility Matrix

| Django Version | Python 3.8 | Python 3.9 | Python 3.10 | Python 3.11 | Python 3.12 |
|---------------|------------|------------|-------------|-------------|-------------|
| 4.2 LTS       | ✅         | ✅         | ✅          | ✅          | ✅          |
| 5.0           | ❌         | ❌         | ✅          | ✅          | ✅          |
| 5.1           | ❌         | ❌         | ✅          | ✅          | ✅          |
| 5.2           | ❌         | ❌         | ✅          | ✅          | ✅          |

## 🎮 Example Project

See the package in action with our complete example project:

```bash
# Clone the repository
git clone https://github.com/jinto/django-i18n-noprefix.git
cd django-i18n-noprefix/example_project

# Install dependencies
pip install django

# Run the demo
./run_demo.sh

# Visit http://localhost:8000
```

The example project includes:
- Multi-language support (English, Korean, Japanese)
- All three language selector styles
- Bootstrap, Tailwind, and Vanilla CSS examples
- Complete translation files
- Production-ready configuration

## 🔍 API Reference

### Middleware

```python
class NoPrefixLocaleMiddleware:
    """
    Replacement for Django's LocaleMiddleware that doesn't use URL prefixes.

    Methods:
        get_language(request) -> str: Detect language from request
        save_language(request, response, language) -> None: Persist language choice
    """
```

### Template Tags

```django
{% load i18n_noprefix %}

<!-- Render language selector -->
{% language_selector [style='dropdown|list|inline'] [next_url='/custom/'] %}

<!-- Get URL for language switch -->
{% switch_language_url 'ko' [next_url='/custom/'] %}

<!-- Check if language is current -->
{{ 'ko'|is_current_language }} → True/False
```

### Views

```python
# URL: /i18n/set-language/<lang_code>/
def change_language(request, lang_code):
    """Change language and redirect."""

# URL: /i18n/set-language-ajax/
def set_language_ajax(request):
    """AJAX endpoint for language change."""
```

### Utility Functions

```python
from django_i18n_noprefix.utils import (
    activate_language,       # Activate language for request
    get_supported_languages, # Get list of language codes
    get_language_choices,    # Get language choices for forms
    is_valid_language,      # Validate language code
)
```

## 🐛 Troubleshooting

### Common Issues and Solutions

**Language not persisting across requests**
- Ensure sessions are enabled in `INSTALLED_APPS` and `MIDDLEWARE`
- Check that cookies are not blocked in the browser
- Verify `NoPrefixLocaleMiddleware` is after `SessionMiddleware`

**Translations not working**
```python
# Check these settings
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / 'locale']

# Run these commands
python manage.py makemessages -l ko
python manage.py compilemessages
```

**Static files not loading**
```bash
python manage.py collectstatic
```

**Middleware order issues**
```python
# Correct order
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # ← First
    'django_i18n_noprefix.middleware.NoPrefixLocaleMiddleware',  # ← Second
    'django.middleware.common.CommonMiddleware',
    # ...
]
```

### Debug Mode

```python
# Enable debug logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django_i18n_noprefix': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 🚀 Performance

- **Zero overhead**: Middleware adds < 0.1ms per request
- **Smart caching**: Language preference cached in session/cookie
- **No database queries**: Pure middleware solution
- **CDN friendly**: No URL prefixes mean better cache utilization

## 🔒 Security Considerations

- CSRF protection on language change endpoints
- XSS safe: All outputs are properly escaped
- Cookie security: Supports Secure, HttpOnly, and SameSite flags
- No user input in URL paths

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Setup development environment
git clone https://github.com/jinto/django-i18n-noprefix.git
cd django-i18n-noprefix
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=django_i18n_noprefix

# Code formatting
black .
ruff check .

# Type checking
mypy django_i18n_noprefix
```

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Credits

Built with ❤️ by [jinto](https://github.com/jinto) and contributors.

Inspired by Django's excellent i18n framework and the needs of real-world multilingual applications.

## 📚 Resources

- [Documentation](https://github.com/jinto/django-i18n-noprefix#readme)
- [PyPI Package](https://pypi.org/project/django-i18n-noprefix/)
- [Issue Tracker](https://github.com/jinto/django-i18n-noprefix/issues)
- [Example Project](https://github.com/jinto/django-i18n-noprefix/tree/main/example_project)
- [Django i18n Documentation](https://docs.djangoproject.com/en/stable/topics/i18n/)

---

**Need help?** [Open an issue](https://github.com/jinto/django-i18n-noprefix/issues) or check our [example project](https://github.com/jinto/django-i18n-noprefix/tree/main/example_project).

**Like this project?** Give it a ⭐ on [GitHub](https://github.com/jinto/django-i18n-noprefix)!
