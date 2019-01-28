from freppledb.common.models import Parameter, Bucket
from freppledb.common.utils import la_time
from freppledb.execute.staging import StagingProcessor
from freppledb.input.enum import ForecastCommentStatus
from freppledb.input.models import ForecastVersion, Forecast
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DemandMdsProcessor(StagingProcessor):
    def __init__(self,
                 with_forecast_version=True,
                 forecast_version_id=None,
                 is_simulation=False,
                 user=None,
                 run_background=True,
                 *args, **kwargs):
        """

        :param with_forecast_version: 是否使用预测版本计算，默认true
        :param forecast_version_id: 制定的计算的预测版本
        :param is_simulation: 是否是模拟计算，默认false
        :param user: 计算用户，默认None
        :param run_background: 是否后台云霞，默认true
        :param args:
        :param kwargs:
           calculate_at:计算时间，默认now
        """
        super(DemandMdsProcessor, self).__init__(user, run_background, args, kwargs)
        self.with_forecast_version = with_forecast_version
        self.forecast_version_id = forecast_version_id
        self.is_simulation = is_simulation

        self.parameter['origin']['with_forecast_version'] = with_forecast_version
        self.parameter['origin']['forecast_version_id'] = forecast_version_id
        self.parameter['origin']['is_simulation'] = is_simulation

    #      self.prepare_input()
    #      self.process()
    #      self.write_output()

    def prepare_input(self, *args, **kwargs):

        print('加载系统参数')

        date_period_type = kwargs.get('demand.calculate.date_period_type', Parameter.getValue(
            'demand.calculate.date_period_type'))
        coverage_period_number = kwargs.get('demand.calculate.date_period_type', Parameter.getValue(
            'demand.calculate.coverage_period_number'))

        plan_leadtime = kwargs.get('demand.calculate.pan_leadtime',
                                   Parameter.getValue('demand.calculate.pan_leadtime'))

        order_fence_time = kwargs.get('demand.calculate.order_fence_time', Parameter.getValue(
            'demand.calculate.order_fence_time'))
        forecast_fence_time = kwargs.get('demand.calculate.forecast_fence_time', Parameter.getValue(
            'demand.calculate.forecast_fence_time'))
        rop_coverage_days = kwargs.get('inventory.rop_coverage_days', Parameter.getValue('inventory.rop_coverage_days'))

        self.parameter['origin']['date_period_type'] = date_period_type
        self.parameter['origin']['coverage_period_number'] = coverage_period_number
        self.parameter['origin']['plan_leadtime'] = plan_leadtime
        self.parameter['origin']['order_fence_time'] = order_fence_time
        self.parameter['origin']['forecast_fence_time'] = forecast_fence_time
        self.parameter['origin']['rop_coverage_days'] = rop_coverage_days

        # 需求开始时间=参数计算时间/当期时间
        self.demand_from_date = Bucket.get_datetime_by_type(
            Bucket.get_nex_time_by_date_type(kwargs.get('calculate_at', datetime.now()), 'd', plan_leadtime),
            date_period_type)

        # 需求结束时间=需求开始时间+需求覆盖周期
        self.demand_end_date = Bucket.get_search_endtime_by_date_type(
            Bucket.get_nex_time_by_date_type(self.demand_from_date, date_period_type, coverage_period_number),
            date_period_type)

        # 设置中间参数
        self.parameter['middle']['demand_from_date'] = self.demand_from_date
        self.parameter['middle']['demand_end_date'] = self.demand_end_date

        forcasts = []
        if self.with_forecast_version:
            # 查找预测
            forecast_version = None
            if self.forecast_version_id is None:
                print('forecast version id 为空')
                # 找到最新的可以使用的forecast
                forecast_version = ForecastVersion.objects.filter(status__in=ForecastCommentStatus.CAN_CALCULATE_MDS_STATUS).order_by('-nr').first()
            else:
                forecast_version = ForecastVersion.objects.filter(nr=self.forecast_version_id).first()
            if forecast_version is None:
                raise Exception('预测版本不存在，无法进行计算')

            # 根据forecast 版本查询预测
            forcasts = Forecast.objects.filter(forecast_version_id=forecast_version.id, parsed_date__range=(self.demand_from_date,self.demand_end_date))
            if not self.is_simulation:
                # 非模拟使用正常释放的forecast
                forcasts = forcasts.filter(status__in=Forecast.CAN_CALCULATE_MDS_STATUS)

        else:
            # 查找所有最新的预测
            forcasts = None




        # 记录参数
        self.log.input_data = self.parameter
