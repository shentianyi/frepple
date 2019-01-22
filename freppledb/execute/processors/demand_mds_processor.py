from freppledb.common.models import Parameter
from freppledb.execute.staging import StagingProcessor
from freppledb.input.enum import ForecastCommentStatus
from freppledb.input.models import ForecastVersion


class DemandMdsProcessor(StagingProcessor):
    def __init__(self, forecast_version_id=None, user_nr=None, *args, **kwargs):
        self.forecast_version_id = forecast_version_id
        super(DemandMdsProcessor, self).__init__(user_nr, args, kwargs)



    def prepare_input(self):
        if self.forecast_version_id is None:
            # 找到最新的可以使用的forecast
            forecast_version = ForecastVersion.objects.filter(status = ForecastCommentStatus.CAN_CALCULATE_MDS_STATUS).order_by('-nr').first()
            # 需求周期
            # 需求时间周期
            demand_bucket_type = Parameter.getValue('demand.plan.bucket_type') | 'W'

            # 需求计算覆盖之间 天数
            demand_coverage_days = Parameter.getValue('demand.plan.coverage_days') | 180
            # 需求计算提前期
            demand_calculate_leadtime = Parameter.getValue('demand.plan.calculate_leadtime') || 3


            if forecast_version:
                forecasts = None