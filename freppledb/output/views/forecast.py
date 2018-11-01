from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncYear
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.utils.translation import ugettext_lazy as _
import dateutil
import datetime
from django.db.models import F

from freppledb.input.models import Forecast


class ForecastCompare(View):
    permissions = (('view_forecast_compare', 'Can view forecast compare'),)

    title = _('forecast compare')

    @classmethod
    def getKey(cls):
        return "%s.%s" % (cls.__module__, cls.__name__)

    @method_decorator(staff_member_required)
    def get(self, request, *args, **kwargs):
        reportkey = ForecastCompare.getKey()
        if request.method == 'GET':
            fmt = request.GET.get('format', None)
            if fmt is None:
                # TODO LA 预测对比
                # template = loader.get_template('output/forecast_compare.html')
                template = 'output/forecast_compare.html'

                context = {
                    'title': self.title,
                    'reportkey': reportkey,
                    'mode': request.GET.get('mode', 'table'),
                    'actions': None,
                    'report_type': request.GET.get('report_type', 'detail')
                }

                return render(request, template, context)
            elif fmt == 'json':
                # 返回JSON数据
                return JsonResponse(self._get_json_data(request), safe=False)
        else:
            raise Http404('PAGE NOT FOUND')

    def _get_json_data(self, request):
        # .extra(select={'item_nr': 'item.nr', 'location_nr': 'location__nr', 'customer_nr': 'customer__nr'}) \

        forecasts = Forecast.objects \
            .annotate(month=TruncMonth('parsed_date')) \
            .extra(select={'t':'normal_qty'})\
            .values('item__nr', 'location__nr', 'customer__nr', 'year', 'month') \
            .annotate(total_value=Sum(F('normal_qty')+F('new_product_plan_qty')+F('promotion_qty'))).first()

        data = {
            'page': 2,
            'records': 100,
            'rows': [
                {'item__nr': 1}
            ],
            'total': 20
        }

        return data
