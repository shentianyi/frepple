from datetime import datetime

import xlrd, csv
from django.views import View
from rest_framework.views import APIView
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from rest_framework import serializers
from freppledb.input.models import Forecast
from django.db import transaction


class ExcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forecast
        filds = '__all__'

    def create(self, validated_data):
        if self.context['action'] == 'create':
            file = self.context['file']
            workbook = xlrd.open_workbook(file)
            table = workbook.sheet_by_index(0)
            nrows = table.nrows
            with transaction.atomic():
                # 创建保存点
                save_point = transaction.savepoint()
                try:
                    for i in range(1, nrows):
                        rowValues = table.row_values(i)  # 读取一行的数据
                        Forecast.objects.create(item=rowValues[0], location=rowValues[1], customer=rowValues[2],
                                                year=rowValues[3])
                        now_version = 'V'+datetime.now().strftime('%Y%m%d%H%M%S')
                        Forecast.version = now_version
                        Forecast.version.save()
                except:
                    transaction.savepoint_rollback(save_point)
                    raise serializers.ValidationError(_('error'))
                else:
                    transaction.savepoint_commit(save_point)

    def update(self, instance, validated_data):
        if self.context['action'] == 'update':
            data = Forecast.objects.aggregate(max('id'))
            old_version = data.version
            if not data:
                return serializers.ValidationError(_('no data to update'))
            else:
                file = self.context['file']
                workbook = xlrd.open_workbook(file)
                table = workbook.sheet_by_index(0)
                nrows = table.nrows
                with transaction.atomic():
                    # 创建保存点
                    save_point = transaction.savepoint()
                    try:
                        for i in range(1, nrows):
                            rowValues = table.row_values(i)  # 读取一行的数据
                            Forecast.objects.create(item=rowValues[0], location=rowValues[1], customer=rowValues[2],
                                                    year=rowValues[3])
                            instance.version = old_version
                            instance.save()
                    except:
                        transaction.savepoint_rollback(save_point)
                        raise serializers.ValidationError(_('error'))
                    else:
                        transaction.savepoint_commit(save_point)


class CsvSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forecast
        filds = '__all__'

    def create(self, validated_data):
        if self.context['action'] == 'create':
            file = self.context['file']
            with open(file) as csvFile:
                table = csv.reader(csvFile)
                with transaction.atomic():
                    # 创建保存点
                    save_point = transaction.savepoint()
                    try:
                        rows = [row for row in table]
                        for rowValues in rows[1:]:
                            Forecast.objects.create(item=rowValues[0], location=rowValues[1], customer=rowValues[2],
                                                    year=rowValues[3])
                            now_version = 'V' + datetime.now().strftime('%Y%m%d%H%M%S')
                            Forecast.version = now_version
                            Forecast.version.save()
                    except:
                        transaction.savepoint_rollback(save_point)
                        raise serializers.ValidationError(_('error'))
                    else:
                        transaction.savepoint_commit(save_point)

    def update(self, instance, validated_data):
        if self.context['action'] == 'update':
            data = Forecast.objects.aggregate(max('id'))
            old_version = data.version
            if not data:
                return serializers.ValidationError(_('no data to update'))

            else:
                file = self.context['file']
                with open(file) as csvFile:
                    table = csv.reader(csvFile)
                    with transaction.atomic():
                        # 创建保存点
                        save_point = transaction.savepoint()
                        try:
                            rows = [row for row in table]
                            for rowValues in rows[1:]:
                                Forecast.objects.create(item=rowValues[0], location=rowValues[1], customer=rowValues[2],
                                                        year=rowValues[3])
                                instance.version = old_version
                                instance.save()
                        except:
                            transaction.savepoint_rollback(save_point)
                            raise serializers.ValidationError(_('error'))
                        else:
                            transaction.savepoint_commit(save_point)


class ForecastVersionView(View):

    def post(self, request, file, date_type, action):
        if request.FILES.name.split('.')[-1] in ['xls', 'xlsx']:
            ser = ExcelSerializer(data=request.data, context={'file': file, 'action': action})
            ser.is_valid(raise_exception=True)

        elif request.FILES.name.split('.')[-1] in ['csv']:
            ser = CsvSerializer(data=request.data, context={'file': file, 'action': action})
            ser.is_valid(raise_exception=True)

        else:
            return HttpResponse(_('Invalid upload request'))
