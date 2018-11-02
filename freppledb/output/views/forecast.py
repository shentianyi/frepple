import calendar
import math
import urllib
from io import BytesIO

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Q, Max
from django.db.models.functions import TruncMonth, TruncYear
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str
from django.views import View
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta

from django.db.models import F
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell

from freppledb.input.models import Forecast, ForecastYear, Item, Location, Customer


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
            report_type = request.GET.get('report_type', 'detail')

            # 详细表头
            reprot_detail_headers = ('物料编号', '地点', '客户代码', '全年计划量', '年初计划量',
                                     '上月预测', '当月预测', '下月预测', '当月VS年初', '当月VS上月', '当月VS下月')
            # 汇总表头
            reprot_aggre_headers = ('物料编号', '地点', '全年计划量', '年初计划量',
                                    '上月预测', '当月预测', '下月预测', '当月VS年初', '当月VS上月', '当月VS下月')
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
            elif fmt in ('spreadsheetlist', 'spreadsheettable', 'spreadsheet'):
                # 下载 excel
                json = self._get_json_data(request, in_page=False)
                wb = Workbook(write_only=True)
                title = '对比报表-%s' % ('详细' if report_type == 'detail' else '汇总')
                ws = wb.create_sheet(title)

                # 写入excel头
                file_headers = reprot_detail_headers if report_type == 'detail' else reprot_aggre_headers
                headers = []
                for h in file_headers:
                    cell = WriteOnlyCell(ws, value=h)
                    headers.append(cell)
                ws.append(headers)

                # 写入表体, 顺序和
                body_fields = ('item__nr','location__nr','customer__nr','total_year_qty','year_qty','last_qty','current_qty','next_qty','current_year_qty','current_last_qty','current_next_qty')
                for data in json['rows']:
                    body = []
                    for field in body_fields:
                        if field in data:
                            cell = WriteOnlyCell(ws,value=data[field])
                            body.append(cell)
                    ws.append(body)

                output = BytesIO()
                wb.save(output)
                response = HttpResponse(
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    content=output.getvalue()
                )
                response['Content-Disposition'] = "attachment; filename*=utf-8''%s.xlsx" % urllib.parse.quote(
                    force_str(title))
                response['Cache-Control'] = "no-cache, no-store"
                return response

            elif fmt in ('csvlist', 'csvtable', 'csv'):
                # 下载 csv
                i = 2
        else:
            raise Http404('PAGE NOT FOUND')

    # TODO 如果预测同时存在 W/M等多个时间度量的情况,不处理?
    # 详细: 根据 item+location+customer分页
    # 汇总: 根据 item+location分页
    # 分页是否准确?
    def _get_json_data(self, request, in_page=True):
        """
        获取json数据, 默认分页,如果不分页,按照分页格式,返回所有数据,可以在下载情景下使用
        :param request:
        :param in_page: 是否分页,默认True
        :return:
        """
        current_date = timezone.now()
        current_year = current_date.year
        current_month = current_date.month

        search_start_time = datetime(current_year - 1, 1, 1) if current_month == 1 else datetime(current_year,
                                                                                                 current_month - 1, 1)

        search_end_time = datetime(current_year + 1, 1, 31, 23, 59, 59, 9999) if current_month == 12 else datetime(
            current_year, current_month + 1, calendar.monthrange(current_year, current_month)[1], 23, 59, 59, 999)

        last_year = current_year - 1 if current_month == 1 else current_year
        last_month = 12 if current_month == 1 else current_month - 1

        next_year = current_year + 1 if current_month == 12 else current_year
        next_month = 1 if current_month == 12 else current_month + 1

        pageObjectsQ = Forecast.objects.annotate(month=TruncMonth('parsed_date')) \
            .filter(parsed_date__range=(search_start_time, search_end_time)) \
            .order_by('item_id', 'location_id', 'customer_id') \
            .values('item_id', 'location_id', 'customer_id') \
            .distinct()

        count = float(pageObjectsQ.count())
        pagesize = request.pagesize if in_page else count
        page = 'page' in request.GET and int(request.GET['page']) or 1
        total_pages = math.ceil(float(count) / pagesize)
        if page > total_pages:
            page = total_pages
        if page < 1:
            page = 1

        cnt = (page - 1) * pagesize + 1

        pageObjects = pageObjectsQ[cnt - 1: cnt + pagesize]

        item_ids = list(set([i['item_id'] for i in pageObjects]))
        location_ids = list(set([i['location_id'] for i in pageObjects]))
        customer_ids = list(set([i['customer_id'] for i in pageObjects]))

        items = Item.objects.filter(id__in=item_ids).values('id', 'nr')
        locations = Location.objects.filter(id__in=location_ids).values('id', 'nr')
        customers = Customer.objects.filter(id__in=customer_ids).values('id', 'nr')
        #
        #
        foreact_query = Forecast.objects \
            .annotate(month=TruncMonth('parsed_date')) \
            .values('item_id', 'location_id', 'customer_id', 'year', 'month') \
            .filter(parsed_date__range=(search_start_time, search_end_time),
                    item_id__in=item_ids,
                    location_id__in=location_ids,
                    customer_id__in=customer_ids) \
            .filter(~Q(status='cancel')) \
            .annotate(version=Max('version_id')) \
            .annotate(qty=Sum((F('normal_qty') + F('new_product_plan_qty') + F('promotion_qty')) * F('ratio') / 100)) \
            # .order_by('-version_id')

        forecastyear_query = ForecastYear.objects \
            .annotate(month=TruncMonth('parsed_date')) \
            .values('item_id', 'location_id', 'customer_id', 'year', 'month') \
            .filter(parsed_date__range=(search_start_time, search_end_time),
                    item_id__in=item_ids,
                    location_id__in=location_ids,
                    customer_id__in=customer_ids) \
            .annotate(qty=Sum((F('normal_qty') + F('new_product_plan_qty') + F('promotion_qty')) * F('ratio') / 100))

        foreactyear_total_query = ForecastYear.objects \
            .values('item_id', 'location_id', 'customer_id', 'year') \
            .filter(year=current_year,
                    item_id__in=item_ids,
                    location_id__in=location_ids,
                    customer_id__in=customer_ids) \
            .annotate(qty=Sum((F('normal_qty') + F('new_product_plan_qty') + F('promotion_qty')) * F('ratio') / 100))

        datas = []

        for c in pageObjects:
            data = {
                'year': current_year,
                'month': current_month,
                'item__nr': None,
                'location__nr': None,
                'customer__nr': None,
                'total_year_qty': None,
                'year_qty': None,
                'last_qty': None,
                'current_qty': None,
                'next_qty': None,
                'current_year_qty': None,
                'current_last_qty': None,
                'current_next_qty': None
            }
            # 设置基础值
            for i in items:
                if i['id'] == c['item_id']:
                    data['item__nr'] = i['nr']
                    break

            for i in locations:
                if i['id'] == c['location_id']:
                    data['location__nr'] = i['nr']
                    break

            for i in customers:
                if i['id'] == c['customer_id']:
                    data['customer__nr'] = i['nr']
                    break

            # 全年值
            for i in foreactyear_total_query:
                if i['item_id'] == c['item_id'] \
                        and i['location_id'] == c['location_id'] \
                        and i['customer_id'] == c['customer_id']:
                    data['total_year_qty'] = round(i['qty'], 2)
                    break

            # 年初值
            for i in forecastyear_query:
                if i['item_id'] == c['item_id'] \
                        and i['location_id'] == c['location_id'] \
                        and i['customer_id'] == c['customer_id'] \
                        and i['year'] == current_year and i['month'].month == current_month:
                    data['year_qty'] = round(i['qty'], 2)
                    break

            # 上月值 当月值 下月值
            for i in foreact_query:
                if i['item_id'] == c['item_id'] \
                        and i['location_id'] == c['location_id'] \
                        and i['customer_id'] == c['customer_id']:

                    if i['year'] == last_year and i['month'].month == last_month:
                        data['last_qty'] = round(i['qty'], 2)

                    if i['year'] == current_year and i['month'].month == current_month:
                        data['current_qty'] = round(i['qty'], 2)

                    if i['year'] == next_year and i['month'].month == next_month:
                        data['next_qty'] = round(i['qty'], 2)

            # 对比值
            if data['current_qty'] is not None:
                if data['year_qty'] is not None and data['year_qty'] != 0:
                    data['current_year_qty_value'] = (data['current_qty'] - data['year_qty']) / data['year_qty']
                    data['current_year_qty'] = "{:.2%}".format(data['current_year_qty_value'])

                if data['last_qty'] is not None and data['last_qty'] != 0:
                    data['current_last_qty_value'] = (data['current_qty'] - data['last_qty']) / data['last_qty']
                    data['current_last_qty'] = "{:.2%}".format(data['current_last_qty_value'])

                if data['next_qty'] is not None and data['next_qty'] != 0:
                    data['current_next_qty_value'] = (data['current_qty'] - data['next_qty']) / data['next_qty']
                    data['current_next_qty'] = "{:.2%}".format(data['current_next_qty_value'])

            datas.append(data)

        data = {
            'page': page,
            'records': count,
            'rows': datas,
            'total': total_pages
        }

        return data
