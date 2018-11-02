from django.db import transaction
from django.utils import timezone
from django.utils.encoding import force_text
from freppledb.common.models import User
from openpyxl import load_workbook, Workbook
from openpyxl.styles import NamedStyle, PatternFill
from openpyxl.writer.write_only import WriteOnlyCell
from io import BytesIO
from freppledb.common.dataload import parseExcelWorksheet
from freppledb.common.message.responsemessage import ResponseMessage
from freppledb.input.models import Forecast, Location, Item, Customer, ForecastVersion, ForecastCommentOperation
from openpyxl.cell import cell


class ForecastUploader:
    @classmethod
    def upload_excel(cls, request, model):
        message = ResponseMessage()

        try:
            for name, file in request.FILES.items():
                # print(name)
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
                        forecast.date_type = request.POST['date_type']
                        for k, v in headers_index.items():
                            value = values[v]
                            field_name = headers_field_name[k]

                            if field_name == 'location':
                                forecast.location = Location.objects.using(request.database).get(nr=value)
                            elif field_name == 'item':
                                forecast.item = Item.objects.using(request.database).get(nr=value)
                            elif field_name == 'customer':
                                try:
                                    forecast.customer = Customer.objects.using(request.database).get(nr=value)
                                except Customer.DoesNotExist as e:
                                    print(e)
                                    # forecast.customer = None
                            elif field_name == 'year':
                                forecast.year = value
                            elif field_name == 'date_number':
                                forecast.date_number = value
                            elif field_name == 'normal_qty':
                                forecast.normal_qty = value
                            elif field_name == 'ratio':
                                forecast.ratio = value
                            elif field_name == 'new_product_plan_qty':
                                forecast.new_product_plan_qty = value
                            elif field_name == 'promotion_qty':
                                forecast.promotion_qty = value

                        forecast.create_user = request.user
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
                            # forecast_version.status = ForecastCommentOperation.statuses[0][0]
                            forecast_version.nr = timezone.now().strftime('%y%m%d%H%M%S')
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
                                # excel 中传的字段
                                excel_fields = [v for k, v in headers_field_name.items()]

                                # 可以被更新的字段
                                update_fields = ['date_type', 'ratio', 'normal_qty', 'normal_qty',
                                                 'new_product_plan_qty', 'promotion_qty']
                                for f in forecasts:
                                    # 更新
                                    try:
                                        update_forecast = Forecast.objects.using(request.database).filter(
                                            # version=forecast_version,
                                            version=forecast_version,
                                            location=f.location,
                                            item=f.item,
                                            customer=f.customer,
                                            year=f.year,
                                            date_type=f.date_type,
                                            date_number=f.date_number).latest('id')

                                        # 判断是否在excel中传了值
                                        for field in update_fields:
                                            if field in excel_fields:
                                                setattr(update_forecast, field, getattr(f, field, None))

                                        update_forecast.save()
                                    except Forecast.DoesNotExist as e:
                                        f.version = forecast_version
                                        f.save()

                        message.result = True
                        message.message = '上传成功'
        except Exception as e:
            message.result = False
            message.message = str(e)
        return message


class ForecastDownloader:
    @classmethod
    def download_excel(cls, request, model, output):
        message = ResponseMessage()
        try:
            wb = Workbook()
            # 第一个sheet是ws,不然会自动生成一个sheet表
            ws = wb.worksheets[0]
            title = force_text(model._meta.verbose_name or model.title)
            ws.title = title
            headerstyle = NamedStyle(name="headerstyle")
            headerstyle.fill = PatternFill(fill_type="solid", fgColor='70c4f4')
            wb.add_named_style(headerstyle)

            download_forecast = Forecast.objects.all().order_by('-id')
            if not download_forecast:
                message.result = False
                message.message = '没有下载数据'
            else:
                # 写入表头数据
                header = []
                for field in model._meta.fields:
                    cell = WriteOnlyCell(ws, value=force_text(field).title())
                    cell.style = 'headerstyle'
                    header.append(cell)
                ws.append(header)

                excel_row = 2

                for f in download_forecast:
                    a = str(f.item)
                    print(a)
                    ws.cell(row=excel_row, column=1, value=f.id)
                    ws.cell(row=excel_row, column=2, value=f.item.nr)
                    ws.cell(row=excel_row, column=3, value=f.location.nr)
                    if f.customer:
                        ws.cell(row=excel_row, column=4, value=f.customer.nr)
                    else:
                        ws.cell(row=excel_row, column=4, value=None)
                    ws.cell(row=excel_row, column=5, value=f.year)
                    ws.cell(row=excel_row, column=6, value=f.date_number)
                    ws.cell(row=excel_row, column=7, value=f.date_type)
                    ws.cell(row=excel_row, column=8, value=f.ratio)
                    ws.cell(row=excel_row, column=9, value=f.normal_qty)
                    ws.cell(row=excel_row, column=10, value=f.new_product_plan_qty)
                    ws.cell(row=excel_row, column=11, value=f.promotion_qty)
                    ws.cell(row=excel_row, column=13, value=f.status)
                    ws.cell(row=excel_row, column=14, value=f.create_user.username)
                    ws.cell(row=excel_row, column=15, value=f.version.nr)
                    ws.cell(row=excel_row, column=16, value=f.created_at)
                    ws.cell(row=excel_row, column=17, value=f.updated_at)
                    excel_row += 1

                wb.save(output)
                message.result = True
                message.message = '下载成功'
                message.content = output.getvalue()

        except Exception as e:
            message.message = str(e)
        return message
