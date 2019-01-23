from freppledb.common.models import Parameter, Bucket
from freppledb.common.utils import la_time
from freppledb.execute.staging import StagingProcessor
from freppledb.input.enum import ForecastCommentStatus
from freppledb.input.models import ForecastVersion, Forecast
from datetime import datetime


class DemandMdsProcessor(StagingProcessor):
    def __init__(self,
                 with_forecast_version=True,
                 forecast_version_id=None,
                 is_simulation=False,
                 user=None,
                 run_background=True,
                 *args, **kwargs):

        super(DemandMdsProcessor, self).__init__(user, run_background, args, kwargs)
        self.with_forecast_version = with_forecast_version
        self.forecast_version_id = forecast_version_id
        self.is_simulation = is_simulation

        self.parameter['with_forecast_version'] = with_forecast_version
        self.parameter['forecast_version_id'] = forecast_version_id
        self.parameter['is_simulation'] = is_simulation

    #      self.prepare_input()
    #      self.process()
    #      self.write_output()

    def prepare_input(self, *args, **kwargs):

        print('加载系统参数')

        date_period_type = kwargs.get('demand.calculate.date_period_type', Parameter.getValue(
            'demand.calculate.date_period_type'))
        coverage_period_number = kwargs.get('demand.calculate.date_period_type', Parameter.getValue(
            'demand.calculate.coverage_period_number'))

        pan_leadtime = kwargs.get('demand.calculate.pan_leadtime',
                                                   Parameter.getValue('demand.calculate.pan_leadtime'))

        order_fence_time = kwargs.get('demand.calculate.order_fence_time', Parameter.getValue(
            'demand.calculate.order_fence_time'))
        forecast_fence_time = kwargs.get('demand.calculate.forecast_fence_time', Parameter.getValue(
            'demand.calculate.forecast_fence_time'))
        rop_coverage_days = kwargs.get('inventory.rop_coverage_days', Parameter.getValue('inventory.rop_coverage_days'))

        # 需求开始时间 加上 前置期，获得时间周期的开始时间
        self.demand_from_date = Bucket.get_datetime_by_type(datetime.now(), date_period_type)

        self.parameter['date_period_type'] = date_period_type
        self.parameter['coverage_period_number'] = coverage_period_number
        self.parameter['order_fence_time'] = order_fence_time
        self.parameter['forecast_fence_time'] = forecast_fence_time
        self.parameter['rop_coverage_days'] = rop_coverage_days

        forcasts = []
        if self.with_forecast_version:
            # 查找预测
            forecast_version = None
            if self.forecast_version_id is None:
                print('forecast version id 为空')
                # 找到最新的可以使用的forecast
                forecast_version = ForecastVersion.objects.filter(
                    status=ForecastCommentStatus.CAN_CALCULATE_MDS_STATUS).order_by('-nr').first()
            else:
                forecast_version = ForecastVersion.objects.filter(nr=self.forecast_version_id).first()
            if forecast_version is None:
                raise Exception('预测版本不存在，无法进行计算，请先准备数据')

            # 根据forecast 版本查询预测
            forcasts = Forecast.objects.filter(forecast_version_id=forecast_version.id, )
        else:
        # 查找所有最新的预测

        # 记录参数
        self.log.input_data = self.parameter
