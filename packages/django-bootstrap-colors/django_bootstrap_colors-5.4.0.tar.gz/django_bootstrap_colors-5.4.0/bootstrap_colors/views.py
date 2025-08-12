from django.conf import settings
from django.http import Http404
from django.views.generic import TemplateView


class BootstrapColorsView(TemplateView):
    template_name = 'bootstrap_colors.css'
    content_type = 'text/css'

    def __init__(self, *args, colors=None, **kwargs):
        super().__init__(*args, **kwargs)
        if colors is None:
            self.colors = getattr(settings, 'BOOTSTRAP_THEME_COLORS', None)
        else:
            self.colors = colors

    def get(self, request, *args, **kwargs):
        if not self.colors:
            raise Http404
        return self.render_to_response({'BOOTSTRAP_THEME_COLORS': self.colors})
