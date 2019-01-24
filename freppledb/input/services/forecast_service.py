from django.db import connection

from freppledb.common.models import Bucket
from freppledb.input.services.base_service import BaseService


class ForecastService(BaseService):

    def query_lastest_forecast(self,
                               start_time,
                               end_time,
                               status,
                               *args, **kwargs):
        '''
        查询最新预测详细
        :param start_time: 查询开始时间
        :param end_time: 查询结束时间
        :param status: 状态，数组
        :param args:
        :param kwargs: 特别的查询条件放在kwarg，如kwargs={'item_id':1, 'location_id':1}
        :return:
        '''
        # date_type_full = Bucket.get_extra_trunc_by_shortcut(date_type)
        with connection.cursor() as cursor:
            params = []
            # query = '''select a.customer_id,a.year,a.parsed_date,
            #                    a.normal_qty, a.new_product_plan_qty , a.promotion_qty,a.ratio,a.status from
            #                    forecast as a inner join (select c.item_id,c.location_id, c.customer_id,c.parsed_date,max(c.version_id) as version_id
            #                    from forecast as c
            #                    where c.status in %s and c.parsed_date between %s and %s and c.item_id = %s and c.location_id = %s
            #                    group by c.item_id,c.location_id, c.customer_id, c.parsed_date) as b
            #                    on a.item_id=b.item_id and a.location_id=b.location_id and a.customer_id=b.customer_id and a.parsed_date=b.parsed_date and a.version_id=b.version_id
            #                    where a.status in %s and a.parsed_date between %s and %s and a.item_id = %s and a.location_id = %s
            #                    '''

            query = r'''select a.customer_id,a.year,a.parsed_date,
                               a.normal_qty, a.new_product_plan_qty , a.promotion_qty,a.ratio,a.status from
                               forecast as a inner join (select c.item_id,c.location_id, c.customer_id,c.parsed_date,max(c.version_id) as version_id 
                               from forecast as c
                               where c.status in %s and c.parsed_date between %s and %s '''

            params.append(status)
            params.append(start_time)
            params.append(end_time)

            if 'item_id' in kwargs:
                query += ' and c.item_id =%s'
                params.append(kwargs['item_id'])
            if 'location_id' in kwargs:
                query += ' and c.location_id =%s'
                params.append(kwargs['location_id'])

            query += r'''group by c.item_id,c.location_id, c.customer_id, c.parsed_date) as b
                               on a.item_id=b.item_id and a.location_id=b.location_id and a.customer_id=b.customer_id and a.parsed_date=b.parsed_date and a.version_id=b.version_id
                               where a.status in %s and a.parsed_date between %s and %s '''

            params.append(status)
            params.append(start_time)
            params.append(end_time)

            if 'item_id' in kwargs:
                query += ' and a.item_id =%s'
                params.append(kwargs['item_id'])

            if 'location_id' in kwargs:
                query += ' and a.location_id =%s'
                params.append(kwargs['location_id'])

            cursor.execute(query,
                           params)

            rows = self.dictfetchall(cursor)
            return rows

    def query_lastest_forecast_and_sum_by_item_and_time(self,
                                                        date_type,
                                                        start_time,
                                                        end_time,
                                                        status,
                                                        *args,
                                                        **kwargs):
        '''
        根据item&location&时间对预测进行分组汇总
        :param date_type: 周期类型
        :param start_time:
        :param end_time:
        :param status:
        :param args:
        :param kwargs:
        :return: 返回分组的字典，如
                {‘item_id’:item_id,'location_id':location_id,‘time’:每个周期的时间点,qty:汇总的数量}
        '''
        forecasts = self.query_lastest_forecast(start_time, end_time, status, args, kwargs)
