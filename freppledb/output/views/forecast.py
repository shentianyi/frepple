from django.http import HttpResponse, Http404
from django.views import View
from django.utils.translation import ugettext_lazy as _
from django.template import loader


class ForecastCompare(View):
    permissions = (('view_forecast_compare', 'Can view forecast compare'),)

    title = _('forecast compare')

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            template = loader.get_template('output/forecast_compare.html')
            return HttpResponse(template.render(None, request))
        else:
            raise Http404('PAGE NOT FOUND')


