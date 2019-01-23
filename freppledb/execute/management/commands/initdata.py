#
# Copyright (C) 2018 by frePPLe bvba
#
# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import datetime
import os

from django.apps import apps
from django.conf import settings
from django.core.management.base import CommandError, BaseCommand
from django.core.management.commands import loaddata
from django.db import DEFAULT_DB_ALIAS, connections, transaction
from django.utils.translation import ugettext_lazy as _
from freppledb.common.models import Parameter


class Command(BaseCommand):
    title = _('初始化数据')
    index = 1800
    help_url = 'user-guide/command-reference.html#initdata'

    def add_arguments(self, parser):
        parser.add_argument(
            '--database', default=DEFAULT_DB_ALIAS,
            help='Nominates a specific database to load data from and export results into'
        )

    def handle(self, *args, **options):
        print(options)
        # get the database object
        database = options['database'] or DEFAULT_DB_ALIAS
        if database not in settings.DATABASES:
            raise CommandError("No database settings known for '%s'" % database)

        with transaction.atomic(using=database, savepoint=False):
            print('>>>>>>> 重置系统参数')
            Parameter.objects.using(database).all().delete()

            params = []
            params.append(Parameter(name='demand.calculate.date_period_type', value='W',
                                    value_type='string',description='需求计算的周期类型，如按天/周/月/季度/年，填写D/W/M/Q/Y，默认W'))

            params.append(Parameter(name='demand.calculate.coverage_period_number',
                                    value='52', value_type='int',description='需求计算覆盖的时间周期数，默认52，含义是覆盖52周'))

            params.append(Parameter(name='demand.calculate.pan_leadtime',
                                    value='3', value_type='int',description='需求计算提前天数，默认3，含义是提前3天'))

            params.append(Parameter(name='demand.calculate.order_fence_time', value='0',
                                    value_type='int',description='订单时间窗口数，默认0'))

            params.append(Parameter(name='demand.calculate.forecast_fence_time', value='0',
                                    value_type='int',description='预测时间窗口数，默认为0'))

            params.append(Parameter(name='inventory.rop_coverage_days', value='180', value_type='int',description='ROP覆盖天数，用以ROP计算，默认180'))
            params.append(Parameter(name='inventory.safetystock_coverage_days', value='180',
                                    value_type='int',description='安全覆盖天数，用以计算安全安全库存计算，默认180'))

            Parameter.objects.using(database).bulk_create(params)
