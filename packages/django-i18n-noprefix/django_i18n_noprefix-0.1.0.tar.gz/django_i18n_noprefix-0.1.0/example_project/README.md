# Django i18n No-Prefix Example Project

This is a complete Django project demonstrating the `django-i18n-noprefix` package.

## Features Demonstrated

- ✅ Clean URLs without language prefixes (/en/, /ko/, /ja/)
- ✅ Language switching with session and cookie persistence
- ✅ Three language selector styles (dropdown, list, inline)
- ✅ CSS framework compatibility (Bootstrap 5, Tailwind CSS, Vanilla CSS)
- ✅ Full internationalization with real translations

## Quick Start

### 1. Install Dependencies

From the main project directory (parent of example_project):

```bash
# Using uv (recommended)
uv pip install django

# Or using pip
pip install django
```

### 2. Run the Demo

```bash
cd example_project
./run_demo.sh
```

Or manually:

```bash
cd example_project
python manage.py migrate
python manage.py runserver
```

### 3. Visit the Demo

Open your browser and go to:
- Main site: http://localhost:8000
- Admin panel: http://localhost:8000/admin (if you created a superuser)

## Project Structure

```
example_project/
├── demo/                  # Demo application
│   ├── views.py          # View classes with translations
│   ├── urls.py           # URL patterns
│   └── ...
├── templates/            # HTML templates
│   ├── base.html        # Base layout
│   ├── home.html        # Home page
│   ├── about.html       # About page
│   ├── features.html    # Features demo
│   ├── settings.html    # Language settings
│   └── styles/          # CSS framework demos
│       ├── bootstrap.html
│       ├── tailwind.html
│       └── vanilla.html
├── locale/              # Translation files
│   ├── ko/             # Korean translations
│   └── ja/             # Japanese translations
├── static/             # Static files
└── example_project/    # Django settings
    └── settings.py     # Configured for django-i18n-noprefix
```

## Available Pages

### Main Pages
- **Home** (`/`) - Welcome page with overview
- **About** (`/about/`) - Package information and features
- **Features** (`/features/`) - Interactive feature demonstrations
- **Settings** (`/settings/`) - Language preference management

### Style Demos
- **Bootstrap 5** (`/styles/bootstrap/`) - Bootstrap component styles
- **Tailwind CSS** (`/styles/tailwind/`) - Tailwind utility classes
- **Vanilla CSS** (`/styles/vanilla/`) - Pure CSS with custom properties

## Language Support

The demo includes three languages:
- 🇬🇧 **English** (en) - Default
- 🇰🇷 **Korean** (ko)
- 🇯🇵 **Japanese** (ja)

## Key Configuration

### settings.py

```python
# Our middleware replaces Django's LocaleMiddleware
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_i18n_noprefix.middleware.NoPrefixLocaleMiddleware',  # <-- Our middleware
    # 'django.middleware.locale.LocaleMiddleware',  # <-- Not needed
    ...
]

# Language configuration
LANGUAGES = [
    ('en', 'English'),
    ('ko', 'Korean'),
    ('ja', 'Japanese'),
]

# Add our package to installed apps
INSTALLED_APPS = [
    ...
    'django_i18n_noprefix',
    'demo',
]
```

### URLs Configuration

```python
# example_project/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django_i18n_noprefix.urls')),  # Language switching URLs
    path('', include('demo.urls')),  # Demo app URLs
]
```

## Testing Language Switching

1. **Using Navigation Bar Dropdown**
   - Select a language from the dropdown in the top navigation

2. **Using Footer Inline Selector**
   - Click on language codes (EN, KO, JA) in the footer

3. **Using Settings Page**
   - Go to Settings and use the list-style selector

4. **Direct URL**
   - Visit `/i18n/set-language/ko/` to switch to Korean
   - Visit `/i18n/set-language/ja/` to switch to Japanese
   - Visit `/i18n/set-language/en/` to switch to English

## Adding Translations

To add or modify translations:

```bash
# Create/update translation files
python manage.py makemessages -l ko -l ja

# Edit the .po files in locale/*/LC_MESSAGES/django.po

# Compile translations
python manage.py compilemessages
```

## Customization

### Adding a New Language

1. Add to `LANGUAGES` in settings.py:
   ```python
   LANGUAGES = [
       ('en', 'English'),
       ('ko', 'Korean'),
       ('ja', 'Japanese'),
       ('zh', 'Chinese'),  # New language
   ]
   ```

2. Create translation files:
   ```bash
   python manage.py makemessages -l zh
   ```

3. Translate strings in `locale/zh/LC_MESSAGES/django.po`

4. Compile:
   ```bash
   python manage.py compilemessages
   ```

### Changing Styles

The demo includes three CSS frameworks. To use a different style:

1. Visit the style demo pages to see examples
2. Copy the HTML structure you prefer
3. Include the appropriate CSS file:
   - Bootstrap: `{% static 'i18n_noprefix/css/bootstrap5.css' %}`
   - Tailwind: `{% static 'i18n_noprefix/css/tailwind.css' %}`
   - Vanilla: `{% static 'i18n_noprefix/css/vanilla.css' %}`

## Troubleshooting

### Static Files Not Loading

```bash
python manage.py collectstatic
```

### Translations Not Working

1. Ensure `USE_I18N = True` in settings.py
2. Check that locale files exist
3. Run `python manage.py compilemessages`

### Language Not Persisting

1. Check that sessions are enabled
2. Verify cookies are not blocked
3. Ensure `NoPrefixLocaleMiddleware` is in MIDDLEWARE

## Learn More

- [Package Documentation](https://github.com/jinto/django-i18n-noprefix)
- [Django i18n Documentation](https://docs.djangoproject.com/en/stable/topics/i18n/)

## License

MIT License - Feel free to use this example as a starting point for your own projects.