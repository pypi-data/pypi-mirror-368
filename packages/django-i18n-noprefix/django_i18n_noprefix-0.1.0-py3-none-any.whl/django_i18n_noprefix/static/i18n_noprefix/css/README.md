# Language Selector Styles Guide

This directory contains pre-built CSS styles for the django-i18n-noprefix language selector components. Choose the style that matches your project's CSS framework.

## Available Styles

### 1. Bootstrap 5 (`bootstrap5.css`)
For projects using Bootstrap 5.x

```django
<!-- Include after Bootstrap CSS -->
{% load static %}
<link href="{% static 'i18n_noprefix/css/bootstrap5.css' %}" rel="stylesheet">
```

**Features:**
- Uses Bootstrap CSS variables
- Dark mode support via `data-bs-theme`
- Responsive utilities
- Integrates with Bootstrap components (form-select, list-group, nav-pills)

**Template Usage:**
```django
{% load i18n_noprefix %}

<!-- Add Bootstrap classes to enhance styling -->
<div class="mb-3">
  {% language_selector style='dropdown' %}
</div>

<!-- Or customize with Bootstrap utilities -->
<select class="form-select form-select-sm">
  ...
</select>
```

### 2. Tailwind CSS (`tailwind.css`)
For projects using Tailwind CSS

```django
<!-- Include in your Tailwind config or as standalone -->
{% load static %}
<link href="{% static 'i18n_noprefix/css/tailwind.css' %}" rel="stylesheet">
```

**Features:**
- Component classes using `@apply`
- Utility-first approach
- Dark mode with `dark:` variants
- Responsive with `sm:`, `md:`, `lg:` prefixes

**Template Usage:**
```django
{% load i18n_noprefix %}

<!-- Add .tw class to use pre-built components -->
<div class="i18n-noprefix-selector--dropdown tw">
  {% language_selector style='dropdown' %}
</div>

<!-- Or apply Tailwind utilities directly -->
<select class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
  ...
</select>
```

### 3. Vanilla CSS (`vanilla.css`)
Pure CSS with no framework dependencies

```django
<!-- Standalone CSS, no dependencies -->
{% load static %}
<link href="{% static 'i18n_noprefix/css/vanilla.css' %}" rel="stylesheet">
```

**Features:**
- CSS custom properties for theming
- Automatic dark mode support
- Lightweight (~6KB minified)
- Modern CSS features (Grid, Flexbox, Custom Properties)

**Customization with CSS Variables:**
```css
:root {
  /* Override theme colors */
  --i18n-primary: #your-color;
  --i18n-bg: #your-bg-color;
  --i18n-border: #your-border-color;
  
  /* Adjust spacing */
  --i18n-spacing-md: 1.5rem;
  
  /* Change border radius */
  --i18n-radius: 0.25rem;
}
```

## Usage Examples

### Dropdown Style
```django
{% language_selector style='dropdown' %}
```
- Best for: Header navigation, compact spaces
- Accessibility: Native `<select>` with full keyboard support

### List Style
```django
{% language_selector style='list' %}
```
- Best for: Settings pages, language preference sections
- Accessibility: Clear visual hierarchy, current language indicator

### Inline Style
```django
{% language_selector style='inline' %}
```
- Best for: Footer, horizontal navigation bars
- Accessibility: Compact but clear, good for 2-4 languages

## Customization

### Adding Your Own Styles

1. **Override with Higher Specificity:**
```css
.my-app .i18n-noprefix-selector--dropdown {
  /* Your custom styles */
}
```

2. **Use CSS Variables (Vanilla CSS):**
```css
.language-selector-wrapper {
  --i18n-primary: #custom-color;
  --i18n-radius: 0;
}
```

3. **Extend with Additional Classes:**
```django
<div class="i18n-noprefix-selector--dropdown custom-class">
  {% language_selector %}
</div>
```

## Responsive Design

All styles include mobile-first responsive design:

- **Mobile (<640px):** Full width, larger touch targets
- **Tablet (640px-1024px):** Optimized spacing
- **Desktop (>1024px):** Compact, hover states

## Accessibility Features

All styles include:
- Proper ARIA labels
- Focus indicators
- Keyboard navigation
- Screen reader support
- High contrast mode compatibility

## Dark Mode

### Bootstrap 5
```html
<html data-bs-theme="dark">
```

### Tailwind CSS
```html
<html class="dark">
```

### Vanilla CSS
Automatic with `prefers-color-scheme` or:
```html
<html class="dark">
```

## Browser Support

- Chrome/Edge: Last 2 versions
- Firefox: Last 2 versions
- Safari: Last 2 versions
- Mobile browsers: iOS Safari 14+, Chrome Android

## Performance

| Style | Size (minified) | Size (gzipped) |
|-------|----------------|----------------|
| Bootstrap 5 | ~4KB | ~1.5KB |
| Tailwind | ~5KB | ~1.8KB |
| Vanilla | ~6KB | ~2KB |

## Common Customizations

### Change Dropdown Arrow
```css
.i18n-noprefix-selector__select {
  background-image: url('your-arrow-icon.svg');
}
```

### Add Flag Icons
```css
.i18n-noprefix-selector__item[data-lang="en"]::before {
  content: "🇬🇧 ";
}
.i18n-noprefix-selector__item[data-lang="ko"]::before {
  content: "🇰🇷 ";
}
```

### Custom Animation
```css
.i18n-noprefix-selector__list {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

## Troubleshooting

### Styles Not Loading
1. Ensure `django.contrib.staticfiles` is in `INSTALLED_APPS`
2. Run `python manage.py collectstatic` in production
3. Check static files configuration

### Conflicts with Existing Styles
- Use more specific selectors
- Load this CSS before your custom styles
- Use the vanilla CSS version for minimal conflicts

### Dark Mode Not Working
- Check your HTML element has the correct class/attribute
- Verify CSS custom properties are not being overridden
- Test with `prefers-color-scheme` media query

## Contributing

To add support for another CSS framework:
1. Create a new CSS file in this directory
2. Follow the BEM class structure
3. Include responsive and dark mode support
4. Update this README with usage instructions