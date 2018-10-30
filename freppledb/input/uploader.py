from django.db import transaction
from django.utils import timezone
from openpyxl import load_workbook

from freppledb.common.dataload import parseExcelWorksheet
from freppledb.common.message.responsemessage import ResponseMessage
from freppledb.input.models import Forecast, Location, Item, Customer, ForecastVersion


class ForecastUploader:
    @classmethod
    def upload_excel(cls, request, model):
        message = ResponseMessage()

        try:
            for name, file in request.FILES.items():
                print(name)
                # 读excel
                wb = load_workbook(filename=file, read_only=True, data_only=True)
                # 第一个sheet
                sheet = wb[wb.sheetnames[0]]
                row_count = 0
                row_number = 1
                # 对应表头是在第几列
                headers_index = {}
                # 对应表头与模型field的name
                headers_field_name = {}
                # 所有excel中的forecast
                forecasts = []

                for row in sheet.iter_rows():
                    row_count += 1
                    if row_number == 1:
                        row_number += 1
                        # required_fields = set()
                        # # 获取必须值 & 表头
                        # for field in model._meta.fields:
                        #     if not field.blank and field.default==NOT_PROVIDED and not isinstance(field, AutoField):
                        #      required_fields.add(field.name)

                        # 获取excelheader
                        _headers = [i.value for i in row]
                        index = 0
                        for h in _headers:
                            for field in model._meta.fields:
                                if h == field.name.lower or h == field.verbose_name.lower():
                                    headers_index[h] = index
                                    headers_field_name[h] = field.name
                            index += 1
                    # 取值
                    else:
                        values = [i.value for i in row]
                        none_len = 0
                        for v in values:
                            if v is None:
                                none_len += 1

                        if none_len == len(values):
                            continue

                        forecast = Forecast()
                        for k, v in headers_index.items():
                            value = values[v]
                            field_name = headers_field_name[k]

                            if field_name == 'location':
                                forecast.location = Location.objects.using(request.database).get(nr=value)
                            elif field_name == 'item':
                                forecast.item = Item.objects.using(request.database).get(nr=value)
                            elif field_name == 'customer':
                                forecast.customer = Customer.objects.using(request.database).get(nr=value)
                            elif field_name == 'year':
                                forecast.year = value
                            elif field_name == 'date_number':
                                forecast.date_number = value
                            elif field_name == 'normal_qty':
                                forecast.normal_qty = value
                            elif field_name == 'ratio':
                                forecast.ratio = value

                        forecasts.append(forecast)
                if row_count < 2:
                    message.result = False
                    message.message = '文件没有数据'
                else:
                    with transaction.atomic(using=request.database, savepoint=False):
                        if request.POST['action'] == 'create':
                            # 创建 version
                            forecast_version = ForecastVersion()
                            forecast_version.create_user = request.user
                            forecast_version.created_at = timezone.now
                            forecast_version.status = ForecastVersion.version_status[0][0]
                            forecast_version.nr = timezone.now().strftime('%Y%m%d%H%M%S')
                            forecast_version.save()
                            for f in forecasts:
                                f.version = forecast_version
                            # 创建forecast
                            Forecast.objects.bulk_create(forecasts)
                        elif request.POST['action'] == 'update':
                            # 查找最新的version
                            forecast_version = ForecastVersion.objects.using(request.database).latest('created_at')
                            if forecast_version is None:
                                message.result = False
                                message.message = '版本不存在,不可以更新!'
                            else:
                                excel_fields = [v for k, v in headers_field_name.items()]

                                for f in forecasts:
                                    # 更新
                                    update_forecast = Forecast.objects.using(request.database).filter(
                                        # version=forecast_version,
                                        version=forecast_version,
                                        location=f.location,
                                        item=f.item,
                                        customer=f.customer,
                                        year=f.year,
                                        date_number=f.date_number).latest('id')

                                if update_forecast is None:
                                    # 创建
                                    f.version = forecast_version
                                    f.save()
                                else:
                                    # 判断是否在excel中传了值
                                    if 'date_type' in excel_fields:
                                        update_forecast.date_type = f.date_type
                                    if 'ratio' in excel_fields:
                                        update_forecast.ratio = f.ratio
                                    # 更新
                                    update_forecast.save()

                        message.result = True
                        message.message = '上传成功'
        except Exception as e:
            message.message = str(e)
        return message
