This django app allows to override the primary color and its variants in
bootstrap.

# Usage

-   Add `bootstrap_colors` to `INSTALLED_APPS`
-   Add `path('colors.css', BootstrapColorsView.as_view(), name='colors')` to
    `urls.py`
-   Add `<link rel="stylesheet" type="text/css" href="{% url 'colors' %}">` to
    your template
-   Set `BOOTSTRAP_THEME_COLORS` (Default: `['#0d6efd', '#0b5ed7', '#0a58ca']`)
-   Optional: Configure caching, e.g. by using
    `django.views.decorators.cache.cache_control`

# Alternatives

Bootstrap provides several ways to achieve this:

-   **CSS custom properities**: It would be great if we could just change a few
    custom properties. Unfortunately they are not used in a way that would
    allow that.
-   **Scss variables**: This requires a Scss compiler somewhere in the build
    process which I would like to avoid.
-   **Override CSS**: This is the approach that is used in this package.
    However, it is brittle because the underlying bootstrap code might change.
