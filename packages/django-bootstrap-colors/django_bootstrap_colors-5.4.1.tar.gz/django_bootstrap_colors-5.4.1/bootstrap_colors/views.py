from django.conf import settings
from django.http import Http404
from django.views.generic import TemplateView


class BootstrapColorsView(TemplateView):
    template_name = 'bootstrap_colors.css'
    content_type = 'text/css'
    colors = getattr(settings, 'BOOTSTRAP_THEME_COLORS', None)

    def get(self, request, *args, **kwargs):
        if not self.colors:
            raise Http404
        return self.render_to_response({'BOOTSTRAP_THEME_COLORS': self.colors})
