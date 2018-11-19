import calendar
import csv
import functools
import math
import operator
import random
import urllib
from io import BytesIO, StringIO

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum, Q, Max
from django.db import connections
from django.db.models.functions import TruncMonth, TruncYear
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render
from django.utils import timezone, translation
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str, force_text
from django.utils.formats import get_format
from django.utils.encoding import force_str, smart_str
from django.views import View
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
import json
from django.db.models import F

import freppledb
from freppledb.common import report
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell

from freppledb.common.models import Bucket
from freppledb.common.utils import la_time, la_enum
from freppledb.common.utils.la_field import decimal2calculate
from freppledb.input.models import Forecast, ForecastYear, Item, Location, Customer, ForecastCommentOperation, \
    ItemSupplier, Calendar


class ForecastCompare(View):
    permissions = (('view_forecast_compare', 'Can view forecast compare'),)

    title = _('forecast compare')

    @classmethod
    def getKey(cls):
        return "%s.%s" % (cls.__module__, cls.__name__)

    @method_decorator(staff_member_required)
    def get(self, request, *args, **kwargs):
        reportkey = ForecastCompare.getKey()
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
                'filters': request.GET.get('filters'),
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
            reprot_detail_fields = (
                'item__nr', 'location__nr', 'customer__nr', 'total_year_qty', 'year_qty', 'last_qty', 'current_qty',
                'next_qty', 'current_year_qty', 'current_last_qty', 'current_next_qty')
            reprot_aggre_fields = (
                'item__nr', 'location__nr', 'total_year_qty', 'year_qty', 'last_qty', 'current_qty',
                'next_qty', 'current_year_qty', 'current_last_qty', 'current_next_qty')

            body_fields = reprot_detail_fields if report_type == 'detail' else reprot_aggre_fields
            for data in json['rows']:
                body = []
                for field in body_fields:
                    if field in data:
                        cell = WriteOnlyCell(ws, value=data[field])
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
            sf = StringIO()
            json = self._get_json_data(request, in_page=False)
            title = '对比报表-%s' % ('详细' if report_type == 'detail' else '汇总')
            decimal_separator = get_format('DECIMAL_SEPARATOR', request.LANGUAGE_CODE, True)
            if decimal_separator == ",":
                writer = csv.writer(sf, quoting=csv.QUOTE_NONNUMERIC, delimiter=';')
            else:
                writer = csv.writer(sf, quoting=csv.QUOTE_NONNUMERIC, delimiter=',')
            file_headers = reprot_detail_headers if report_type == 'detail' else reprot_aggre_headers
            writer.writerow(file_headers)

            reprot_detail_fields = (
                'item__nr', 'location__nr', 'customer__nr', 'total_year_qty', 'year_qty', 'last_qty', 'current_qty',
                'next_qty', 'current_year_qty', 'current_last_qty', 'current_next_qty')
            reprot_aggre_fields = (
                'item__nr', 'location__nr', 'total_year_qty', 'year_qty', 'last_qty', 'current_qty',
                'next_qty', 'current_year_qty', 'current_last_qty', 'current_next_qty')

            body_fields = reprot_detail_fields if report_type == 'detail' else reprot_aggre_fields
            for data in json['rows']:
                body = []
                for field in body_fields:
                    if field in data:
                        body.append(data[field])
                writer.writerow(body)

            response = HttpResponse(
                content_type='text/csv; charset=%s' % settings.CSV_CHARSET,
                content=sf.getvalue()
            )
            # Filename parameter is encoded as specified in rfc5987
            response['Content-Disposition'] = "attachment; filename*=utf-8''%s.csv" % urllib.parse.quote(
                force_str(title))
            response['Cache-Control'] = "no-cache, no-store"
            return response

    # TODO 如果预测同时存在 W/M等多个时间度量的情况,不处理?
    #      同时大粒度的时间向小粒度的时间现在不能做很好支持(比如1M转换到4W平均等)
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

        report_type = request.GET.get('report_type', 'detail')
        # 查询条件&时间
        filters = {
            'groupOp': 'AND',
            'rules': []
        }

        if 'filters' in request.GET:
            filters = json.loads(request.GET.get('filters'))

        current_date = timezone.now()
        current_year = int(self._get_query_filter(filters, 'year', current_date.year)['data'])  # current_date.year
        current_month = int(self._get_query_filter(filters, 'month', current_date.month)['data'])

        last_datetime = la_time.last_month_time(current_date)
        next_datetime = la_time.next_month_time(current_date)

        search_start_time = la_time.month_search_starttime(last_datetime)
        search_end_time = la_time.month_search_endtime(next_datetime)

        last_year = last_datetime.year
        last_month = last_datetime.month

        next_year = next_datetime.year
        next_month = next_datetime.month

        filter_fields = ('item__nr', 'location__nr', 'customer__nr')
        q_filters = [Q(**{'parsed_date__range': (search_start_time, search_end_time)})]

        for rule in self._get_query_filters(filters, filter_fields):
            op, field, data = rule['op'], rule['field'], rule['data']
            filter_fmt, exclude = freppledb.common.report.GridReport._filter_map_jqgrid_django[op]
            filter_str = smart_str(filter_fmt % {'field': field})

            if filter_fmt.endswith('__in'):
                filter_kwargs = {filter_str: data.split(',')}
            else:
                filter_kwargs = {filter_str: smart_str(data)}

            if exclude:
                q_filters.append(~Q(**filter_kwargs))
            else:
                q_filters.append(Q(**filter_kwargs))

        # 分页计算
        page_group_fields = ['item_id', 'location_id']

        if report_type == 'detail':
            page_group_fields.append('customer_id')

        pageObjectsQ = Forecast.objects.annotate(month=TruncMonth('parsed_date')) \
            .filter(functools.reduce(operator.iand, q_filters)) \
            .order_by(*page_group_fields) \
            .values(*page_group_fields) \
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

        item_ids = (0,) if count == 0 else tuple(set([i['item_id'] for i in pageObjects]))
        location_ids = (0,) if count == 0 else tuple(set([i['location_id'] for i in pageObjects]))
        if report_type == 'detail':
            customer_ids = (0,) if count == 0 else tuple(set([i['customer_id'] for i in pageObjects]))

        items = Item.objects.filter(id__in=item_ids).values('id', 'nr')
        locations = Location.objects.filter(id__in=location_ids).values('id', 'nr')
        if report_type == 'detail':
            customers = Customer.objects.filter(id__in=customer_ids).values('id', 'nr')
        #
        #
        # foreact_query = Forecast.objects \
        #     .annotate(month=TruncMonth('parsed_date')) \
        #     .values('item_id', 'location_id', 'customer_id', 'year', 'month') \
        #     .filter(parsed_date__range=(search_start_time, search_end_time),
        #             item_id__in=item_ids,
        #             location_id__in=location_ids,
        #             customer_id__in=customer_ids) \
        #     .filter(~Q(status='cancel')) \
        #     .annotate(version=Max('version_id')) \
        #     .annotate(qty=Sum((F('normal_qty') + F('new_product_plan_qty') + F('promotion_qty')) * F('ratio') / 100)) \
        #     # .order_by('-version_id')

        # 年初查询主查询
        forecast_query_values = ['item_id', 'location_id', 'year', 'month_num']
        forecast_query_total_values = ['item_id', 'location_id']

        forecast_year_filters = []
        forecast_year_filters.append(Q(**{'parsed_date__range': (search_start_time, search_end_time)}))
        forecast_year_filters.append(Q(**{'item_id__in': item_ids}))
        forecast_year_filters.append(Q(**{'location_id__in': location_ids}))

        if report_type == 'detail':
            forecast_query_values.append('customer_id')
            forecast_query_total_values.append('customer_id')
            forecast_year_filters.append(Q(**{'customer_id__in': customer_ids}))

        forecastyear_query = ForecastYear.objects \
            .annotate(month_num=TruncMonth('parsed_date')) \
            .values(*forecast_query_values) \
            .filter(functools.reduce(operator.iand, forecast_year_filters)) \
            .annotate(qty=Sum((F('normal_qty') * F('ratio') / 100 + F('new_product_plan_qty') + F('promotion_qty'))))

        foreactyear_total_query = ForecastYear.objects \
            .values(*forecast_query_total_values) \
            .filter(functools.reduce(operator.iand, forecast_year_filters)) \
            .annotate(qty=Sum((F('normal_qty') * F('ratio') / 100 + F('new_product_plan_qty') + F('promotion_qty'))))

        # 预测查询
        cursor = connections[request.database].cursor()
        if report_type == 'detail':
            forecast_query = '''
                select a.item_id,a.location_id,a.customer_id,a.year,DATE_TRUNC('month',a.parsed_date) as month_num,
                SUM(((a.normal_qty*a.ratio/100 + a.new_product_plan_qty) + a.promotion_qty)) AS qty from
                forecast as a inner join (select c.item_id,c.location_id,c.customer_id,c.parsed_date,max(c.version_id) as version_id 
                from forecast as c
                where c.status in %s and c.parsed_date between %s and %s and c.item_id in %s and c.location_id in %s and c.customer_id in %s
                group by c.item_id,c.location_id,c.customer_id,c.parsed_date) as b
                on a.item_id=b.item_id and a.location_id=b.location_id and a.customer_id=b.customer_id and a.parsed_date=b.parsed_date and a.version_id=b.version_id
                where a.status in %s and a.parsed_date between %s and %s and a.item_id in %s and a.location_id in %s  and a.customer_id in %s
                group by a.item_id,a.location_id,a.customer_id,a.year,month_num
                '''

            cursor.execute(forecast_query,
                           [ForecastCommentOperation.compare_report_status, search_start_time, search_end_time,
                            item_ids, location_ids,
                            customer_ids, ForecastCommentOperation.compare_report_status, search_start_time,
                            search_end_time,
                            item_ids, location_ids, customer_ids])
        else:
            forecast_query = '''
                            select a.item_id,a.location_id,a.customer_id,a.year,DATE_TRUNC('month',a.parsed_date) as month_num,
                            SUM(((a.normal_qty*a.ratio/100 + a.new_product_plan_qty) + a.promotion_qty)) AS qty from
                            forecast as a inner join (select c.item_id,c.location_id,c.customer_id,c.parsed_date,max(c.version_id) as version_id 
                            from forecast as c
                            where c.status in %s and c.parsed_date between %s and %s and c.item_id in %s and c.location_id in %s
                            group by c.item_id,c.location_id,c.customer_id,c.parsed_date) as b
                            on a.item_id=b.item_id and a.location_id=b.location_id and a.customer_id=b.customer_id and a.parsed_date=b.parsed_date and a.version_id=b.version_id
                            where a.status in %s and a.parsed_date between %s and %s and a.item_id in %s and a.location_id in %s
                            group by a.item_id,a.location_id,a.customer_id,a.year,month_num
                            '''
            cursor.execute(forecast_query,
                           [ForecastCommentOperation.compare_report_status, search_start_time, search_end_time,
                            item_ids,
                            location_ids, ForecastCommentOperation.compare_report_status, search_start_time,
                            search_end_time,
                            item_ids, location_ids])

        datas = []
        rows = [x for x in cursor.fetchall()]

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

            if report_type == 'detail':
                for i in customers:
                    if i['id'] == c['customer_id']:
                        data['customer__nr'] = i['nr']
                        break

            # 全年值
            for i in foreactyear_total_query:
                if (report_type == 'detail' and i['item_id'] == c['item_id'] \
                    and i['location_id'] == c['location_id'] \
                    and i['customer_id'] == c['customer_id']) \
                        or (report_type == 'aggre' and i['item_id'] == c['item_id'] \
                            and i['location_id'] == c['location_id']):
                    data['total_year_qty'] = round(i['qty'], 2)
                    break

            # 年初值
            for i in forecastyear_query:
                if (report_type == 'detail' and i['item_id'] == c['item_id'] \
                    and i['location_id'] == c['location_id'] \
                    and i['customer_id'] == c['customer_id'] \
                    and i['year'] == current_year and i['month_num'].month == current_month) \
                        or (report_type == 'aggre' and i['item_id'] == c['item_id'] \
                            and i['location_id'] == c['location_id'] \
                            and i['year'] == current_year and i['month_num'].month == current_month):
                    data['year_qty'] = round(i['qty'], 2)
                    break

            # 上月值 当月值 下月值
            for row in rows:

                i = {
                    'item_id': row[0],
                    'location_id': row[1],
                    'customer_id': row[2],
                    'year': row[3],
                    'month_num': row[4],
                    'qty': row[5]
                }
                if (report_type == 'detail' and i['item_id'] == c['item_id'] \
                    and i['location_id'] == c['location_id'] \
                    and i['customer_id'] == c['customer_id']) \
                        or (report_type == 'aggre' and i['item_id'] == c['item_id'] \
                            and i['location_id'] == c['location_id']):

                    if i['year'] == last_year and i['month_num'].month == last_month:
                        if data['last_qty'] is None:
                            data['last_qty'] = 0
                        data['last_qty'] += round(i['qty'], 2)

                    if i['year'] == current_year and i['month_num'].month == current_month:
                        if data['current_qty'] is None:
                            data['current_qty'] = 0
                        data['current_qty'] += round(i['qty'], 2)

                    if i['year'] == next_year and i['month_num'].month == next_month:
                        if data['next_qty'] is None:
                            data['next_qty'] = 0
                        data['next_qty'] += round(i['qty'], 2)
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

    def _get_query_filter(self, filters, key, default_value=None):
        for f in filters['rules']:
            for k, v in f.items():
                if k == 'field' and v == key:
                    return f
        return {'op': 'eq', 'field': key, 'data': default_value}

    def _get_query_filters(self, filters, keys):
        fs = []
        for key in keys:
            for f in filters['rules']:
                for k, v in f.items():
                    if k == 'field' and v == key:
                        fs.append(f)
        return fs


# TODO
# 1. 配额系数的平均计算, 先查出来的sum(ration) S和count(ratio) C个数. 再计算sum(S)/sum(C). 取两位小数
class ForecastItem(View):
    permissions = (('view_forecast_item', 'Can view forecast item'),)

    title = _('forecast item')

    @method_decorator(staff_member_required())
    def get(self, request, *args, **kwargs):
        item = Item.objects.filter(id=request.GET.get('id', None)).first()
        location = Location.objects.filter(id=request.GET.get('location_id', None)).first()

        if item is None or location is None:
            return JsonResponse({"result": False, "code": 200, "message": "参数错误,数据未找到"}, safe=False)

        # 初始化时间类型, 默认周
        date_type = request.GET.get('date_type', 'W')
        if date_type.isspace():
            date_type = "W"
        date_type_full = Bucket.get_extra_trunc_by_shortcut(date_type)

        # 初始化查询时间
        search_start_time = request.GET.get('start_time', None)
        search_start_time = la_time.string2dt(
            search_start_time) if search_start_time else Bucket.get_search_starttime_by_date_type(
            la_time.last_n_year_time(datetime.now(), 2), date_type)

        search_end_time = request.GET.get('end_time', None)
        search_end_time = la_time.string2dt(
            search_end_time) if search_end_time else Bucket.get_search_endtime_by_date_type(
            la_time.next_n_year_time(datetime.now(), 2), date_type)

        # 查詢
        cursor = connections[request.database].cursor()

        forecast_query = '''select a.customer_id,a.year,DATE_TRUNC(%s,a.parsed_date) as trunc_parsed_date,
                               a.normal_qty, a.new_product_plan_qty , a.promotion_qty,a.ratio from
                               forecast as a inner join (select c.customer_id,c.parsed_date,max(c.version_id) as version_id 
                               from forecast as c
                               where c.status in %s and c.parsed_date between %s and %s and c.item_id = %s and c.location_id = %s
                               group by c.customer_id, c.parsed_date) as b
                               on a.customer_id=b.customer_id and a.parsed_date=b.parsed_date and a.version_id=b.version_id
                               where a.status in %s and a.parsed_date between %s and %s and a.item_id = %s and a.location_id = %s
                               '''
        cursor.execute(forecast_query,
                       [date_type_full, ForecastCommentOperation.compare_report_status, search_start_time,
                        search_end_time,
                        item.id,
                        location.id, ForecastCommentOperation.compare_report_status, search_start_time,
                        search_end_time,
                        item.id, location.id])

        # 返回值
        message = {
            "result": True,
            "code": 200,
            "message": None,
            "content": {
                "location": {
                    "id": location.id,
                    "nr": location.nr,
                    "name": location.name
                },
                "data": []
            },

        }

        # 获取查询所有数据
        rows = cursor.fetchall()
        # 根据查询的开始时间,查询的结束时间, 计算出时间(列名称)
        start_time = Bucket.get_datetime_by_type(search_start_time, date_type)
        end_time = Bucket.get_datetime_by_type(search_end_time, date_type)

        while start_time <= end_time:
            data = {
                "x_value": start_time,
                "x_text": Bucket.get_x_time_name(start_time, date_type),
                "y": {
                    "total": 0,
                    "last_sale_qty": 0,
                    "actual_sale_qty": 0,  # TODO forecast sale qty, CMARK
                    "system_forecast_qty": 0,  # TODO forecast sale qt, CMARK
                    "ratio": 0,
                    "normal_qty": 0,
                    "new_product_plan_qty": 0,
                    "promotion_qty": 0,
                    "_row_count": 0
                }
            }

            # 赋值
            for row in rows:
                if start_time == row[2]:
                    data['y']['normal_qty'] += decimal2calculate(row[3])
                    data['y']['new_product_plan_qty'] += decimal2calculate(row[4])
                    data['y']['promotion_qty'] += decimal2calculate(row[5])
                    data['y']['ratio'] += decimal2calculate(row[6])
                    data['y']['_row_count'] += 1
                    data['y']['total'] += decimal2calculate(
                        round(decimal2calculate(row[3]) * decimal2calculate(row[6]) / 100, 2) + decimal2calculate(
                            row[4]) + decimal2calculate(row[5]))

            # 计算配比
            if data['y']['_row_count'] > 0:
                data['y']['ratio'] = decimal2calculate(data['y']['ratio'] / data['y']['_row_count'])

            message['content']['data'].append(data)
            # 下一个值
            start_time = Bucket.get_nex_time_by_date_type(start_time, date_type)

        return JsonResponse(message, encoder=DjangoJSONEncoder, safe=False)


class ForecastItemGraph(View):
    permissions = (('view_forecast_item_graph', 'Can view forecast item graph'),)

    title = _('forecast item graph')

    @method_decorator(staff_member_required())
    def get(self, request, *args, **kwargs):
        item = Item.objects.filter(id=request.GET.get('id', None)).first()
        location = Location.objects.filter(id=request.GET.get('location_id', None)).first()

        if item is None or location is None:
            return JsonResponse({"result": False, "code": 404, "message": "参数错误,数据未找到"}, safe=False)

        # 初始化时间类型, 默认周
        date_type = request.GET.get('date_type', 'W')
        if date_type.isspace():
            date_type = "W"
        date_type_full = Bucket.get_extra_trunc_by_shortcut(date_type)

        # 初始化查询时间
        search_start_time = request.GET.get('start_time', None)
        search_start_time = la_time.string2dt(
            search_start_time) if search_start_time else Bucket.get_search_starttime_by_date_type(
            la_time.last_n_year_time(datetime.now(), 2), date_type)

        search_end_time = request.GET.get('end_time', None)
        search_end_time = la_time.string2dt(
            search_end_time) if search_end_time else Bucket.get_search_endtime_by_date_type(
            la_time.next_n_year_time(datetime.now(), 2), date_type)

        cursor = connections[request.database].cursor()

        forecast_query = '''select a.customer_id,a.year,DATE_TRUNC(%s,a.parsed_date) as trunc_parsed_date,
                               a.normal_qty, a.new_product_plan_qty , a.promotion_qty,a.ratio from
                               forecast as a inner join (select c.customer_id,c.parsed_date,max(c.version_id) as version_id 
                               from forecast as c
                               where c.status in %s and c.parsed_date between %s and %s and c.item_id = %s and c.location_id = %s
                               group by c.customer_id, c.parsed_date) as b
                               on a.customer_id=b.customer_id and a.parsed_date=b.parsed_date and a.version_id=b.version_id
                               where a.status in %s and a.parsed_date between %s and %s and a.item_id = %s and a.location_id = %s
                               '''
        cursor.execute(forecast_query,
                       [date_type_full, ForecastCommentOperation.compare_report_status, search_start_time,
                        search_end_time,
                        item.id,
                        location.id, ForecastCommentOperation.compare_report_status, search_start_time,
                        search_end_time,
                        item.id, location.id])

        # 返回值
        message = {
            "result": True,
            "code": 200,
            "message": "相应数据查询成功",
            "content": {
                "current_time_point": {},
                "serials": [
                    {
                        "serial": "Dispatches(Forecast basis)",
                        "serial_type": "FORECAST BASIS",
                        "points": []
                    },
                    {
                        "serial": "Demand forecast",
                        "serial_type": "DEMAND FORECAST",
                        "points": []
                    }

                ]
            }
        }
        # 获取查询所有数据
        rows = cursor.fetchall()
        # 根据查询的开始时间,查询的结束时间, 计算出时间(列名称)
        start_time = Bucket.get_datetime_by_type(search_start_time, date_type)
        end_time = Bucket.get_datetime_by_type(search_end_time, date_type)
        current = datetime.now()
        current_time = datetime(current.year, current.month, current.day)
        current_text = Bucket.get_x_time_name(current_time, date_type)
        current = {
            "x_value": current_time,
            "x_text": current_text,
            "y": None
        }
        message['content']['current_time_point'] = current

        while start_time < current_time:
            dispatches_points = {
                "x_value": start_time,
                "x_text": Bucket.get_x_text_name(start_time, date_type),
                "y": 0
            }
            forecast_points = {
                "x_value": start_time,
                "x_text": Bucket.get_x_text_name(start_time, date_type),
                "y": 0
            }

            total = 0
            # 赋值
            for row in rows:
                if start_time == row[2]:
                    total += round(decimal2calculate(row[3]) * decimal2calculate(row[6]) / 100, 2) + decimal2calculate(
                        row[4]) + decimal2calculate(row[5])

            dispatches_points["y"] = total
            message["content"]["serials"][0]["points"].append(dispatches_points)
            message["content"]["serials"][1]["points"].append(forecast_points)

            # 下一个值
            start_time = Bucket.get_nex_time_by_date_type(start_time, date_type)

        while current_time <= end_time:
            dispatches_points = {
                "x_value": current_time,
                "x_text": Bucket.get_x_text_name(current_time, date_type),
                "y": 0
            }
            forecast_points = {
                "x_value": current_time,
                "x_text": Bucket.get_x_text_name(current_time, date_type),
                "y": 0
            }
            total = 0
            # 赋值
            for row in rows:
                if current_time == row[2]:
                    total += round(decimal2calculate(row[3]) * decimal2calculate(row[6]) / 100, 2) + decimal2calculate(
                        row[4]) + decimal2calculate(row[5])

            forecast_points["y"] = total
            message["content"]["serials"][0]["points"].append(dispatches_points)
            message["content"]["serials"][1]["points"].append(forecast_points)
            # 下一个值
            current_time = Bucket.get_nex_time_by_date_type(current_time, date_type)

        return JsonResponse(message, encoder=DjangoJSONEncoder, safe=False)


class PlanItemGraph(View):
    permissions = (('view_plan_item_graph', 'Can view plan item graph'),)

    title = _('plan item graph')

    @method_decorator(staff_member_required())
    def get(self, request, *args, **kwargs):
        item = Item.objects.filter(id=request.GET.get('id', None)).first()
        item_supplier = ItemSupplier.objects.filter(item=request.GET.get('id', None), effective_start__lte=datetime.now(),
                                               effective_end__gte=datetime.now()).order_by('priority', '-ratio',
                                                                                           'id').first()

        location = Location.objects.filter(id=request.GET.get('location_id', None)).first()

        if item is None or location is None:
            return JsonResponse({"result": False, "code": 404, "message": "参数错误,数据未找到"}, safe=False)

        # 初始化时间类型, 默认周
        date_type = request.GET.get('date_type', 'W')
        if date_type.isspace():
            date_type = "W"
        date_type_full = Bucket.get_extra_trunc_by_shortcut(date_type)

        # 初始化查询时间
        search_start_time = request.GET.get('start_time', None)
        search_start_time = la_time.string2dt(
            search_start_time) if search_start_time else Bucket.get_search_starttime_by_date_type(
            la_time.last_n_year_time(datetime.now(), 2), date_type)

        search_end_time = request.GET.get('end_time', None)
        search_end_time = la_time.string2dt(
            search_end_time) if search_end_time else Bucket.get_search_endtime_by_date_type(
            la_time.next_n_year_time(datetime.now(), 2), date_type)

        start_time = Bucket.get_datetime_by_type(search_start_time, date_type)
        end_time = Bucket.get_datetime_by_type(search_end_time, date_type)
        current = datetime.now()
        current_time = datetime(current.year, current.month, current.day)
        current_text = Bucket.get_x_time_name(current_time, date_type)

        if item_supplier is None:
            lead_time = 0
        else:
            lead_time_num = item_supplier.wd2cd()
            lead_time = current_time + relativedelta(days=lead_time_num)

        current = {
            "x_value": current_time,
            "x_text": current_text,
            "y": None
        }
        lead_time_point = {
            "x_value": lead_time,
            "x_text": Bucket.get_x_time_name(lead_time, date_type),
            "y": None

        }

        # 返回值
        message = {
            "result": True,
            "code": 200,
            "message": "相应数据查询成功",
            "content": {
                "current_time_point": current,
                "lead_time_point": lead_time_point,
                "serials": [
                    {
                        "serial": "预测",
                        "serial_type": "FORECAST",
                        "points": []
                    }

                ]
            }
        }

        cursor = connections[request.database].cursor()

        forecast_query = '''select a.customer_id,a.year,DATE_TRUNC(%s,a.parsed_date) as trunc_parsed_date,
                               a.normal_qty, a.new_product_plan_qty , a.promotion_qty,a.ratio from
                               forecast as a inner join (select c.customer_id,c.parsed_date,max(c.version_id) as version_id 
                               from forecast as c
                               where c.status in %s and c.parsed_date between %s and %s and c.item_id = %s and c.location_id = %s
                               group by c.customer_id, c.parsed_date) as b
                               on a.customer_id=b.customer_id and a.parsed_date=b.parsed_date and a.version_id=b.version_id
                               where a.status in %s and a.parsed_date between %s and %s and a.item_id = %s and a.location_id = %s
                               '''
        cursor.execute(forecast_query,
                       [date_type_full, ForecastCommentOperation.compare_report_status, search_start_time,
                        search_end_time,
                        item.id,
                        location.id, ForecastCommentOperation.compare_report_status, search_start_time,
                        search_end_time,
                        item.id, location.id])

        rows = cursor.fetchall()
        while start_time < current_time:
            forecast_points = {
                "x_value": start_time,
                "x_text": Bucket.get_x_text_name(start_time, date_type),
                "y": 0
            }

            message["content"]["serials"][0]["points"].append(forecast_points)
            # 下一个值
            start_time = Bucket.get_nex_time_by_date_type(start_time, date_type)

        while current_time <= end_time:
            forecast_points = {
                "x_value": current_time,
                "x_text": Bucket.get_x_text_name(current_time, date_type),
                "y": 0
            }
            total = 0
            # 赋值
            for row in rows:
                if current_time == row[2]:
                    total += round(decimal2calculate(row[3]) * decimal2calculate(row[6]) / 100, 2) + decimal2calculate(
                        row[4]) + decimal2calculate(row[5])

            forecast_points["y"] = -total
            message["content"]["serials"][0]["points"].append(forecast_points)
            # 下一个值
            current_time = Bucket.get_nex_time_by_date_type(current_time, date_type)

        return JsonResponse(message, encoder=DjangoJSONEncoder, safe=False)


# 单个物料模拟列表
class ItemBufferOperateRecords(View):
    permissions = (('view_buffer_operate_records', 'Can view buffer operate records'),)

    title = _('buffer operate records')

    @method_decorator(staff_member_required())
    def get(self, request, *args, **kwargs):
        item = Item.objects.filter(id=request.GET.get('id', None)).first()
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 100)
        if item is None:
            return JsonResponse({"result": False, "code": 200, "message": "参数错误,数据未找到"}, safe=False)

        message = {
            "page": page,
            "records": 200,
            "total": 1,
            "rows": []
        }
        data = {
            "date_number": 0,
            "qty": 0,
            "move_types": 0,
            "name": 0,
            "order_num": 0,
            "order_line_num": 0,
            "buffer": 0
        }

        for i in range(0, 200):
            data = {
                "date_number": random.randint(1, 100),
                "qty": random.randint(1, 100),
                "move_types": random.randint(1, 100),
                "name": random.randint(1, 100),
                "order_num": random.randint(1, 100),
                "order_line_num": random.randint(1, 100),
                "buffer": random.randint(1, 100)
            }
            i += 1
            message["rows"].append(data)
        return JsonResponse(message, encoder=DjangoJSONEncoder, safe=False)
