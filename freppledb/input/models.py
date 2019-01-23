#
# Copyright (C) 2007-2013 by frePPLe bvba
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

from datetime import datetime, time
from functools import reduce

from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone

from django.db import models, DEFAULT_DB_ALIAS
from django.db.models import Max
from django.utils.translation import ugettext_lazy as _

from freppledb.common.fields import JSONBField, AliasDateTimeField
from freppledb.common.models import HierarchyModel, AuditModel, MultiDBManager, User, Comment
from freppledb.common.utils import la_time
from freppledb.common.utils.la_calendar import normal_calendar
from freppledb.input import enum

searchmode = (
    ('PRIORITY', _('priority')),
    ('MINCOST', _('minimum cost')),
    ('MINPENALTY', _('minimum penalty')),
    ('MINCOSTPENALTY', _('minimum cost plus penalty'))
)


class Calendar(AuditModel):
    # Database fields
    # . Translators: Translation included with Django
    name = models.CharField(_('name'), max_length=300, primary_key=True)

    defaultvalue = models.DecimalField(
        _('default value'), max_digits=20,
        decimal_places=8, default=0, null=True, blank=True,
        help_text=_('Value to be used when no entry is effective')
    )
    description = models.CharField(
        _('description'), max_length=500, null=True,
        blank=True
    )
    category = models.CharField(
        _('category'), max_length=300, null=True,
        blank=True, db_index=True
    )
    subcategory = models.CharField(
        _('subcategory'), max_length=300,
        null=True, blank=True, db_index=True
    )

    max_cd_cal_steps = 999

    @classmethod
    def cd(cls, calendar, start_date, work_days):
        """
        计算 calendar day
        :param calendar: 日历对象,
        :param start_date: 开始日期
        :param work_days: 工作日天数
        :return:
        """
        day = int((start_date + relativedelta(days=1)).strftime("%w"))

        adict = {0: 'sunday', 1: 'monday', 2: 'tuesday', 3: 'wednesday', 4: 'thursday', 5: 'friday', 6: 'saturday'}
        if calendar:
            cd_days = 1
            buckets = calendar.buckets.order_by('priority').all()

            work_days_find = 0

            while work_days_find < work_days and cd_days < cls.max_cd_cal_steps:
                bucket = None
                for b in buckets:
                    if b.startdate <= start_date <= b.enddate:
                        bucket = b
                        break

                if bucket:
                    if getattr(bucket, adict[day], False):
                        work_days_find += 1

                start_date = start_date + relativedelta(days=1)
                cd_days += 1

            return cd_days
        else:
            return normal_calendar(start_date, work_days)

    def __str__(self):
        return self.name

    class Meta(AuditModel.Meta):
        db_table = 'calendar'
        # . Translators: Translation included with Django
        verbose_name = _('calendar')
        # . Translators: Translation included with Django
        verbose_name_plural = _('calendars')
        ordering = ['name']


class CalendarBucket(AuditModel):
    # Database fields
    id = models.AutoField(_('identifier'), primary_key=True)
    # . Translators: Translation included with Django
    calendar = models.ForeignKey(
        Calendar, verbose_name=_('calendar'), related_name='buckets',
        on_delete=models.CASCADE
    )
    startdate = models.DateField(_('start date'), null=True, blank=True)
    enddate = models.DateField(_('end date'), null=True, blank=True, default=datetime(2030, 12, 31))
    value = models.DecimalField(
        _('value'), default=0, blank=True,
        max_digits=20, decimal_places=8
    )
    priority = models.IntegerField(_('priority'), default=0, blank=True, null=True)

    # . Translators: Translation included with Django
    monday = models.BooleanField(_('Monday'), blank=True, default=True)
    # . Translators: Translation included with Django
    tuesday = models.BooleanField(_('Tuesday'), blank=True, default=True)
    # . Translators: Translation included with Django
    wednesday = models.BooleanField(_('Wednesday'), blank=True, default=True)
    # . Translators: Translation included with Django
    thursday = models.BooleanField(_('Thursday'), blank=True, default=True)
    # . Translators: Translation included with Django
    friday = models.BooleanField(_('Friday'), blank=True, default=True)
    # . Translators: Translation included with Django
    saturday = models.BooleanField(_('Saturday'), blank=True, default=True)
    # . Translators: Translation included with Django
    sunday = models.BooleanField(_('Sunday'), blank=True, default=True)
    starttime = models.TimeField(_('start time'), blank=True, null=True, default=time(0, 0, 0))
    endtime = models.TimeField(_('end time'), blank=True, null=True, default=time(23, 59, 59))

    class Manager(MultiDBManager):
        def get_by_natural_key(self, calendar, startdate, enddate, priority):
            return self.get(
                calendar=calendar, startdate=startdate, enddate=enddate, priority=priority
            )

    def natural_key(self):
        return (self.calendar, self.startdate, self.enddate, self.priority)

    objects = Manager()

    def __str__(self):
        return "%s" % self.id

    class Meta(AuditModel.Meta):
        ordering = ['calendar', 'id']
        db_table = 'calendarbucket'
        verbose_name = _('calendar bucket')
        verbose_name_plural = _('calendar buckets')
        unique_together = (('calendar', 'startdate', 'enddate', 'priority'),)


# TODO CHARLOT
class Location(AuditModel, HierarchyModel):
    # 设置外键显示的值
    display_key = 'nr'
    # 设置外键导入的值
    foreign_input_key = 'nr'

    # Database fields
    # 添加自增列
    id = models.AutoField(_('id'), help_text=_('Unique identifier'), primary_key=True)

    nr = models.CharField(_('nr'), max_length=300, db_index=True, unique=True)

    # 设置name为非主键
    name = models.CharField(_('name'), max_length=300, primary_key=False, db_index=True)

    # 地区
    area = models.CharField(_('area'), max_length=300, db_index=True, null=True, blank=True)

    available = models.ForeignKey(
        Calendar, verbose_name=_('available'),
        null=True, blank=True, on_delete=models.CASCADE,
        help_text=_('Calendar defining the working hours and holidays'),
    )

    category = models.CharField(
        _('category'), max_length=300, null=True, blank=True, db_index=True
    )

    subcategory = models.CharField(
        _('subcategory'), max_length=300, null=True, blank=True, db_index=True
    )

    description = models.CharField(
        _('description'), max_length=500, null=True, blank=True
    )

    # CMARK 下拉框的显示值是这个返回的
    def __str__(self):
        return self.nr

    # CMARK 上传时,使用以下判断是否可以使用
    class Manager(MultiDBManager):
        def get_by_natural_key(self, nr):
            return self.get(nr=nr)

    # def natural_key(self):
    #     return (self.nr,)

    # CMARK 定义自然key, 在创建/编辑的过程中, 可以使用这个键来做查询
    # 　比如上传时，id(主键)是非必须的，所有通过natural_key 查询, 如果填写了id就使用id做查询
    natural_key = ('nr',)

    # 设置manager 这个要和get_by_natural_key一起使用!
    objects = Manager()

    class Meta(AuditModel.Meta):
        db_table = 'location'
        verbose_name = _('location')
        verbose_name_plural = _('locations')
        ordering = ['id']


class Customer(AuditModel, HierarchyModel):
    # Database fields
    # 设置外键显示的值
    display_key = 'nr'
    # 设置外键导入的值
    foreign_input_key = 'nr'
    # 设置owner显示的值
    # owner_display_key = 'nr'
    id = models.AutoField(_('id'), help_text=_('Unique identifier'), primary_key=True)
    nr = models.CharField(_('customer nr'), max_length=300, db_index=True, unique=True)
    name = models.CharField(_('name'), max_length=300, primary_key=False, db_index=True)
    area = models.CharField(_('area'), max_length=300, db_index=True, null=True, blank=True)
    address = models.CharField(_('address'), max_length=300, db_index=True, null=True, blank=True)
    ship_address = models.CharField(_('ship address'), max_length=300, db_index=True, null=True, blank=True)
    available = models.ForeignKey(
        Calendar, verbose_name=_('available'),
        null=True, blank=True, on_delete=models.CASCADE,
        help_text=_('Calendar defining the working hours and holidays')
    )
    description = models.CharField(
        _('description'), max_length=500, null=True, blank=True
    )
    category = models.CharField(
        _('category'), max_length=300, null=True, blank=True, db_index=True
    )
    subcategory = models.CharField(
        _('subcategory'), max_length=300, null=True, blank=True, db_index=True
    )

    def __str__(self):
        return self.nr

    # CMARK 上传时,使用以下判断是否可以使用
    class Manager(MultiDBManager):
        def get_by_natural_key(self, nr):
            return self.get(nr=nr)

    # CMARK 定义自然key, 在创建/编辑的过程中, 可以使用这个键来做查询
    # 　比如上传时，id(主键)是非必须的，所有通过natural_key 查询, 如果填写了id就使用id做查询
    natural_key = ('nr',)

    # 设置manager 这个要和get_by_natural_key一起使用!
    objects = Manager()

    class Meta(AuditModel.Meta):
        db_table = 'customer'
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
        ordering = ['id']


class Item(AuditModel, HierarchyModel):
    # type_status = {'FG': enum.FgStatus.to_tuple(), 'RM': enum.RmStatus.to_tuple(), 'WIP': ()}

    # Database fields
    # 设置外键显示的值
    display_key = 'nr'
    # 设置外键导入的值
    foreign_input_key = 'nr'
    id = models.AutoField(_('id'), help_text=_('Unique identifier'), primary_key=True)
    nr = models.CharField(_('item nr'), max_length=300, db_index=True, unique=True)
    name = models.CharField(_('name'), max_length=300, primary_key=False, db_index=True)
    barcode = models.CharField(_('barcode'), max_length=300, db_index=True, null=True, blank=True)
    type = models.CharField(_('type'), max_length=20, choices=enum.ItemType.to_tuple(), null=False, blank=False)
    status = models.CharField(_('status'), max_length=20, null=True, blank=True, choices=enum.FgStatus.to_tuple())
    plan_strategy = models.CharField(_('plan strategy'), max_length=20, null=True, blank=True,
                                     choices=enum.ItemProductStrategy.to_tuple())
    lock_type = models.CharField(_('lock type'), max_length=20, null=True, blank=True, choices=enum.LockType.to_tuple(),
                                 default="unlocked")
    lock_expire_at = models.DateField(_('lock expire at'), null=True, blank=True)
    price_abc = models.CharField(_('price abc'), max_length=20, null=True, blank=True, choices=enum.AbcType.to_tuple())
    qty_abc = models.CharField(_('qty abc'), max_length=20, null=True, blank=True, choices=enum.AbcType.to_tuple())

    cost = models.DecimalField(
        _('cost'), null=True, blank=True,
        max_digits=20, decimal_places=8,
        help_text=_("Cost of the item")
    )
    gross_weight = models.DecimalField(_('gross weight'), max_digits=20, decimal_places=8, null=True, blank=True)
    net_weight = models.DecimalField(_('net weight'), max_digits=20, decimal_places=8, null=True, blank=True)
    physical_unit = models.CharField(_('physical unit'), max_length=20, null=True, blank=True)
    project_nr = models.CharField(_('project nr'), max_length=300, primary_key=False, db_index=True, null=True,
                                  blank=True, )
    mpq = models.DecimalField(_('mpq'), max_digits=20, decimal_places=8, null=True, blank=True)
    outer_package_num = models.IntegerField(_('outer package num'), null=True, blank=True)
    pallet_num = models.IntegerField(_('pallet num'), null=True, blank=True)
    outer_package_gross_weight = models.DecimalField(_('outer package gross weight'), max_digits=20, decimal_places=8,
                                                     null=True, blank=True)
    pallet_gross_weight = models.DecimalField(_('pallet gross weight'), max_digits=20, decimal_places=8, null=True,
                                              blank=True)
    outer_package_volume = models.DecimalField(_('outer package volume'), max_digits=20, decimal_places=8, null=True,
                                               blank=True)
    pallet_volume = models.DecimalField(_('pallet volume'), max_digits=20, decimal_places=8, null=True, blank=True)
    plan_list_date = models.DateField(_('plan list date'), db_index=True, null=True, blank=True, )
    plan_delist_date = models.DateField(_('plan delist date'), db_index=True, null=True, blank=True)
    category = models.CharField(_('category'), max_length=300, null=True, blank=True, db_index=True)
    subcategory = models.CharField(_('subcategory'), max_length=300, null=True, blank=True, db_index=True)
    description = models.CharField(_('description'), max_length=500, null=True, blank=True)

    def __str__(self):
        return self.nr

    # CMARK 上传时,使用以下判断是否可以使用
    class Manager(MultiDBManager):
        def get_by_natural_key(self, nr):
            return self.get(nr=nr)

    # CMARK 定义自然key, 在创建/编辑的过程中, 可以使用这个键来做查询
    # 　比如上传时，id(主键)是非必须的，所有通过natural_key 查询, 如果填写了id就使用id做查询
    natural_key = ('nr',)

    # 设置manager 这个要和get_by_natural_key一起使用!
    objects = Manager()

    class Meta(AuditModel.Meta):
        db_table = 'item'
        verbose_name = _('item')
        verbose_name_plural = _('items')
        ordering = ['id']


class ItemLocation(AuditModel):
    """物料地点"""
    id = models.AutoField(_('id'), help_text=_('Unique identifier'), primary_key=True)
    item = models.ForeignKey(
        Item, verbose_name=_('item'),
        db_index=True, related_name='itemlocation_item',
        null=False, blank=False, on_delete=models.CASCADE)

    location = models.ForeignKey(
        Location, verbose_name=_('location'),
        db_index=True, related_name='itemlocation_location',
        null=False, blank=False, on_delete=models.CASCADE)
    type = models.CharField(_('type'), max_length=20, choices=enum.ItemType.to_tuple(), null=False, blank=False)
    status = models.CharField(_('status'), max_length=20, null=True, blank=True, choices=enum.FgStatus.to_tuple())
    plan_strategy = models.CharField(_('plan strategy'), max_length=20, null=True, blank=True,
                                     choices=enum.ItemProductStrategy.to_tuple())
    lock_type = models.CharField(_('lock type'), max_length=20, null=True, blank=True, choices=enum.LockType.to_tuple(),
                                 default="unlocked")
    lock_expire_at = models.DateField(_('lock expire at'), null=True, blank=True)
    inventory_qty = models.DecimalField(_('inventory qty'), max_digits=20, decimal_places=8, null=True, blank=True)
    available_inventory = models.DecimalField(_('available inventory'), max_digits=20, decimal_places=8, null=True,
                                              blank=True)
    inventory_cost = models.DecimalField(_('inventory cost'), max_digits=20, decimal_places=8, null=True, blank=True)
    price_abc = models.CharField(_('price abc'), max_length=20, null=True, blank=True, choices=enum.AbcType.to_tuple())
    qty_abc = models.CharField(_('qty abc'), max_length=20, null=True, blank=True, choices=enum.AbcType.to_tuple())

    cost = models.DecimalField(
        _('cost'), null=True, blank=True,
        max_digits=20, decimal_places=8)
    gross_weight = models.DecimalField(_('gross weight'), max_digits=20, decimal_places=8, null=True, blank=True)
    net_weight = models.DecimalField(_('net weight'), max_digits=20, decimal_places=8, null=True, blank=True)
    physical_unit = models.CharField(_('physical unit'), max_length=20, null=True, blank=True)
    project_nr = models.CharField(_('project nr'), max_length=300, primary_key=False, db_index=True, null=True,
                                  blank=True, )
    moq = models.DecimalField(_('MOQ'), max_digits=20, decimal_places=8)

    order_unit_qty = models.DecimalField(_('order unit qty'), max_digits=20, decimal_places=8, default=0)
    order_max_qty = models.DecimalField(_('order max qty'), max_digits=20, decimal_places=8, default=0)
    product_time = models.DecimalField(_('product time'), max_digits=20, decimal_places=8, default=0, null=True,
                                       blank=True)
    load_time = models.DecimalField(_('load time'), null=True, max_digits=20, decimal_places=8, default=0,
                                    blank=True)
    transit_time = models.DecimalField(_('transit time'), max_digits=20, decimal_places=8, default=0, null=True,
                                       blank=True)
    receive_time = models.DecimalField(_('receive time'), max_digits=20, decimal_places=8, default=0, null=True,
                                       blank=True)
    mpq = models.DecimalField(_('mpq'), max_digits=20, decimal_places=8, null=True, blank=True)
    earliest_order_date = models.DateField(_('earliest order date'), null=True, blank=True)
    plan_supplier_date = models.DateField(_('plan supplier date'), null=True, blank=True)
    plan_load_date = models.DateField(_('plan load date'), null=True, blank=True)
    plan_receive_date = models.DateField(_('plan receive date'), null=True, blank=True)

    outer_package_num = models.IntegerField(_('outer package num'), null=True, blank=True)
    pallet_num = models.IntegerField(_('pallet num'), null=True, blank=True)
    outer_package_gross_weight = models.DecimalField(_('outer package gross weight'), max_digits=20, decimal_places=8,
                                                     null=True, blank=True)
    pallet_gross_weight = models.DecimalField(_('pallet gross weight'), max_digits=20, decimal_places=8, null=True,
                                              blank=True)
    outer_package_volume = models.DecimalField(_('outer package volume'), max_digits=20, decimal_places=8, null=True,
                                               blank=True)
    pallet_volume = models.DecimalField(_('pallet volume'), max_digits=20, decimal_places=8, null=True, blank=True)
    plan_list_date = models.DateField(_('plan list date'), db_index=True, null=True, blank=True, )
    plan_delist_date = models.DateField(_('plan delist date'), db_index=True, null=True, blank=True)
    category = models.CharField(_('category'), max_length=300, null=True, blank=True, db_index=True)
    subcategory = models.CharField(_('subcategory'), max_length=300, null=True, blank=True, db_index=True)
    description = models.CharField(_('description'), max_length=500, null=True, blank=True)

    def __str__(self):
        return '%s - %s' % (
            self.item.nr if self.item else 'No item',
            self.location.nr if self.location else 'Any location'
        )

    class Manager(MultiDBManager):
        def get_by_natural_key(self, item, location):
            return self.get(item=item, location=location)

    def natural_key(self):
        return self.item, self.location

    objects = Manager()

    class Meta(AuditModel.Meta):
        db_table = 'itemlocation'
        verbose_name = _('item location')
        verbose_name_plural = _('item locations')
        unique_together = (('item', 'location'),)
        ordering = ['id']

    def wd2cd(self):
        calendar = self.location.available
        return Calendar.cd(calendar, datetime.now().date(), self.total_wds())

    def total_wds(self):
        return reduce(lambda x, y: x + y, map(lambda x: x if x else 0,
                                              [self.product_time, self.load_time, self.transit_time,
                                               self.receive_time]))


class ItemCustomer(AuditModel):
    id = models.AutoField(_('id'), help_text=_('Unique identifier'), primary_key=True)
    sale_item = models.ForeignKey(
        Item, verbose_name=_('sale item'),
        db_index=True, related_name='itemcustomer_sale_item',
        null=False, blank=False, on_delete=models.CASCADE)

    product_item = models.ForeignKey(
        Item, verbose_name=_('product item'),
        db_index=True, related_name='itemcustomer_product_item',
        null=False, blank=False, on_delete=models.CASCADE)

    customer = models.ForeignKey(
        Customer, verbose_name=_('customer'),
        db_index=True, related_name='itemcustomer_customer',
        null=False, blank=False, on_delete=models.CASCADE)

    location = models.ForeignKey(
        Location, verbose_name=_('location'),
        db_index=True, related_name='itemcustomer_location',
        null=False, blank=False, on_delete=models.CASCADE)
    customer_item_nr = models.CharField(_('customer item nr'), max_length=300, null=True, blank=True, db_index=True)
    status = models.CharField(_('status'), max_length=20, null=True, blank=True, choices=enum.FgStatus.to_tuple())
    lock_type = models.CharField(_('lock type'), max_length=20, null=True, blank=True, choices=enum.LockType.to_tuple())
    lock_expire_at = models.DateField(_('lock expire at'), null=True, blank=True)
    plan_list_date = models.DateField(_('plan list date'), db_index=True, null=True, blank=True)
    plan_delist_date = models.DateField(_('plan delist date'), db_index=True, null=True, blank=True)
    effective_start = models.DateTimeField(
        _('effective start'), null=True, blank=True,
        help_text=_('Validity start date'))
    effective_end = models.DateTimeField(
        _('effective end'), null=True, blank=True,
        help_text=_('Validity end date'))

    # CMARK 的显示值是这个返回的
    def __str__(self):
        return '%s - %s -%s -%s' % (
            self.sale_item.nr if self.sale_item else 'No item',
            self.product_item.nr if self.product_item else 'No product item',
            self.customer.nr if self.customer else 'No client',
            self.location.nr if self.location else 'Any location'
        )

    class Manager(MultiDBManager):
        def get_by_natural_key(self, sale_item, product_item, customer, location):
            return self.get(item=sale_item, product_item=product_item, client=customer, location=location)

    def natural_key(self):
        return self.sale_item, self.product_item, self.customer, self.location

    objects = Manager()

    class Meta(AuditModel.Meta):
        db_table = 'itemcustomer'
        verbose_name = _('item customer')
        verbose_name_plural = _('item customers')
        unique_together = (('sale_item', 'product_item', 'customer', 'location'),)
        ordering = ['id']


class ItemSuccessor(AuditModel):
    # Database fields
    # 设置外键导入的值
    # foreign_input_key = 'nr'

    id = models.AutoField(_('id'), help_text=_('Unique identifier'), primary_key=True)
    item = models.ForeignKey(
        Item, verbose_name=_('item'),
        db_index=True, related_name='itemsuccessors_item',
        null=False, blank=False, on_delete=models.CASCADE)

    item_successor = models.ForeignKey(
        Item, verbose_name=_('item successor'),
        db_index=True, related_name='itemsuccessor_successor',
        null=False, blank=False, on_delete=models.CASCADE)
    relation_type = models.CharField(_('relation type'), max_length=20, choices=enum.RelationType.to_tuple(),
                                     null=False, blank=False)
    priority = models.IntegerField(_('priority'), default=0)
    ratio = models.DecimalField(
        _('ratio'), max_digits=20, decimal_places=8, default=100,
    )

    effective_start = models.DateTimeField(
        _('effective start'), null=True, blank=True,
        help_text=_('Validity start date'))
    effective_end = models.DateTimeField(
        _('effective end'), null=True, blank=True,
        help_text=_('Validity end date'))

    def __str__(self):
        # return '%s - %s - %s' % (
        return '%s - %s' % (
            self.item.nr if self.item else 'No item',
            self.item_successor.nr if self.item_successor else 'No item successor',
        )

    class Manager(MultiDBManager):
        def get_by_natural_key(self, item, item_successor):
            return self.get(item=item, item_successor=item_successor)

    def natural_key(self):
        return (self.item, self.item_successor)

    objects = Manager()

    class Meta(AuditModel.Meta):
        db_table = 'itemsuccessor'
        verbose_name = _('item successor')
        verbose_name_plural = _('item successors')

        ordering = ['id']


class Operation(AuditModel):
    id = models.AutoField(_('id'), primary_key=True)
    nr = models.CharField(_('nr'), max_length=300, db_index=True, unique=True)
    name = models.CharField(_('name'), max_length=300, primary_key=False, db_index=True)
    type = models.CharField(
        _('type'), max_length=20, null=True, blank=True, choices=enum.OperationType.to_tuple())

    location = models.ForeignKey(Location, verbose_name=_('location'), related_name='operation_location',
                                 on_delete=models.CASCADE)
    category = models.CharField(
        _('category'), max_length=300, null=True, blank=True, db_index=True
    )
    subcategory = models.CharField(
        _('subcategory'), max_length=300, null=True, blank=True, db_index=True
    )
    min_num_per = models.DecimalField(
        _('min num per'), max_digits=20, decimal_places=8,
        null=True, blank=True, default=1.0,
        help_text=_("A minimum quantity for operationplans")
    )
    max_num_per = models.DecimalField(
        _('max num per'), null=True, blank=True,
        max_digits=20, decimal_places=8,
        help_text=_("A maximum quantity for operationplans")
    )
    multiple_per = models.DecimalField(
        _('multiple per'), null=True, blank=True,
        max_digits=20, decimal_places=8,
        help_text=_("A multiple quantity for operationplans")
    )
    cost_per = models.DecimalField(
        _('cost'), null=True, blank=True,
        max_digits=20, decimal_places=8,
        help_text=_("Cost per operationplan unit")
    )
    duration_per = models.DurationField(
        _('duration per unit'), null=True, blank=True,
        help_text=_("A variable duration for the operation")
    )
    available = models.ForeignKey(
        Calendar, verbose_name=_('available'),
        null=True, blank=True, on_delete=models.CASCADE,
        help_text=_('Calendar defining the working hours and holidays')
    )
    effective_start = models.DateTimeField(
        _('effective start'), null=True, blank=True,
        help_text=_('Validity start date')
    )
    effective_end = models.DateTimeField(
        _('effective end'), null=True, blank=True,
        help_text=_('Validity end date')
    )
    alternative_process_mode = models.CharField(
        _('alternative process mode'), max_length=20, null=True, blank=True, choices=enum.OperationMode.to_tuple())

    # fence = models.DurationField(
    #     _('release fence'), null=True, blank=True,
    #     help_text=_(
    #         "Operationplans within this time window from the current day are expected to be released to production ERP")
    # )
    # posttime = models.DurationField(
    #     _('post-op time'), null=True, blank=True,
    #     help_text=_("A delay time to be respected as a soft constraint after ending the operation")
    # )
    # duration = models.DurationField(
    #     _('duration'), null=True, blank=True,
    #     help_text=_("A fixed duration for the operation")
    # )
    # search = models.CharField(
    #     _('search mode'), max_length=20,
    #     null=True, blank=True, choices=searchmode,
    #     help_text=_('Method to select preferred alternate')
    # )

    def __str__(self):
        return self.nr

    class Manager(MultiDBManager):
        def get_by_natural_key(self, location, available):
            return self.get(location=location, available=available)

    def natural_key(self):
        return (self.location, self.available)

    objects = Manager()

    # def __str__(self):
    #     return '%s - %s' % (
    #         self.location.nr if self.location else 'No location',
    #         self.available.name if self.available else 'No calendar',
    #     )

    class Meta(AuditModel.Meta):
        db_table = 'operation'
        verbose_name = _('operation')
        verbose_name_plural = _('operations')
        ordering = ['id']


class SubOperation(AuditModel):
    # Database fields
    id = models.AutoField(_('identifier'), primary_key=True)
    parent_operation = models.ForeignKey(
        Operation, verbose_name=_('parent operation'),
        related_name='suboperations', help_text=_("Parent operation"),
        on_delete=models.CASCADE
    )
    suboperation = models.ForeignKey(
        Operation, verbose_name=_('suboperation'),
        related_name='superoperations', help_text=_("Child operation"),
        on_delete=models.CASCADE
    )
    priority = models.IntegerField(
        _('priority'), default=1,
        help_text=_("Sequence of this operation among the suboperations. Negative values are ignored.")
    )
    effective_start = models.DateTimeField(
        _('effective start'), null=True, blank=True,
        help_text=_("Validity start date")
    )
    effective_end = models.DateTimeField(
        _('effective end'), null=True, blank=True,
        help_text=_("Validity end date")
    )

    class Manager(MultiDBManager):
        def get_by_natural_key(self, parent_operation, suboperation, effective_start):
            return self.get(parent_operation=parent_operation, suboperation=suboperation,
                            effective_start=effective_start)

    def natural_key(self):
        return (self.parent_operation, self.suboperation)

    objects = Manager()

    def __str__(self):
        return ("%s   %s   %s" % (
            self.parent_operation.nr if self.parent_operation else None,
            self.priority,
            self.suboperation.nr if self.suboperation else None
        ))

    class Meta(AuditModel.Meta):
        db_table = 'suboperation'
        # ordering = ['parent_operation', 'priority', 'suboperation']
        ordering = ['id']
        verbose_name = _('suboperation')
        verbose_name_plural = _('suboperations')
        unique_together = (('parent_operation', 'suboperation', 'effective_start'),)


class Buffer(AuditModel):
    # Fields common to all buffer types
    name = models.CharField(_('name'), max_length=300, primary_key=True,
                            help_text=_('Unique identifier'))
    description = models.CharField(
        _('description'), max_length=500, null=True, blank=True
    )
    category = models.CharField(
        _('category'), max_length=300, null=True, blank=True, db_index=True
    )
    subcategory = models.CharField(
        _('subcategory'), max_length=300, null=True, blank=True, db_index=True
    )
    type = models.CharField(
        _('type'), max_length=20, null=True, blank=True, choices=enum.CommonType.to_tuple(),
        default='default'
    )
    location = models.ForeignKey(
        Location, verbose_name=_('location'), db_index=True, blank=False,
        null=False, on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        Item, verbose_name=_('item'), db_index=True, blank=False,
        null=False, on_delete=models.CASCADE
    )
    onhand = models.DecimalField(
        _('onhand'), null=True, blank=True,
        max_digits=20, decimal_places=8,
        default="0.00", help_text=_('current inventory')
    )
    minimum = models.DecimalField(
        _('minimum'), null=True, blank=True,
        max_digits=20, decimal_places=8,
        default="0.00", help_text=_('safety stock')
    )
    minimum_calendar = models.ForeignKey(
        Calendar, verbose_name=_('minimum calendar'),
        null=True, blank=True, on_delete=models.CASCADE,
        help_text=_('Calendar storing a time-dependent safety stock profile')
    )
    min_interval = models.DurationField(
        _('min_interval'), null=True, blank=True,
        help_text=_('Batching window for grouping replenishments in batches')
    )

    class Manager(MultiDBManager):
        def get_by_natural_key(self, item, location):
            return self.get(item=item, location=location)

    def natural_key(self):
        return (self.item, self.location)

    objects = Manager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = "%s @ %s" % (
            self.item.name if self.item else "NULL", self.location.nr if self.location else "NULL")
        # Call the real save() method
        super(Buffer, self).save(*args, **kwargs)

    class Meta(AuditModel.Meta):
        db_table = 'buffer'
        verbose_name = _('buffer')
        verbose_name_plural = _('buffers')
        ordering = ['name']
        unique_together = (('item', 'location'),)


class InventoryParameter(AuditModel):
    """库存参数"""

    id = models.AutoField(_('id'), help_text=_('Unique identifier'), primary_key=True)
    item = models.ForeignKey(
        Item, verbose_name=_('item'),
        related_name='inventoryparameter_item',
        null=False, blank=False, on_delete=models.CASCADE)

    location = models.ForeignKey(
        Location, verbose_name=_('location'),
        related_name='inventoryparameter_location',
        null=False, blank=False, on_delete=models.CASCADE)
    rop_cover_period = models.IntegerField(_('rop cover period'))
    safetystock_cover_period = models.IntegerField(_('safetystock cover period'))
    safetysotck_min_qty = models.DecimalField(_('safety sotck min qty'), max_digits=20, decimal_places=8)
    safetysotck_max_qty = models.DecimalField(_('safety sotck max qty'), max_digits=20, decimal_places=8)
    safetystock_qty_by_system = models.DecimalField(_('system safety stock'), max_digits=20, decimal_places=8)
    service_level = models.DecimalField(_('service level'), max_digits=20, decimal_places=8)

    class Manager(MultiDBManager):
        def get_by_natural_key(self, item, location):
            return self.get(item=item, location=location)

    def natural_key(self):
        return self.item, self.location

    objects = Manager()

    def __str__(self):
        return "%s - %s" % (
            self.item.nr if self.item else None,
            self.location.nr if self.location else None
        )

    class Meta(AuditModel.Meta):
        db_table = 'inventoryparameter'
        verbose_name = _('inventory parameter')
        verbose_name_plural = _('inventory parameters')
        ordering = ['id']
        unique_together = (('item', 'location'),)


class SetupMatrix(AuditModel):
    # Database fields
    id = models.AutoField(_('id'), help_text=_('Unique identifier'), primary_key=True)

    nr = models.CharField(_('nr'), max_length=300, db_index=True, unique=True)

    name = models.CharField(_('name'), max_length=300)

    category = models.CharField(
        _('category'), max_length=300, null=True, blank=True, db_index=True
    )
    subcategory = models.CharField(
        _('subcategory'), max_length=300, null=True, blank=True, db_index=True
    )

    class Manager(MultiDBManager):
        def get_by_natural_key(self, nr):
            return self.get(nr=nr)

    def natural_key(self):
        return (self.nr)

    objects = Manager()

    def __str__(self):
        return self.nr

    class Meta(AuditModel.Meta):
        db_table = 'setupmatrix'
        verbose_name = _('setup matrix')
        verbose_name_plural = _('setup matrices')
        ordering = ['name']


class SetupRule(AuditModel):
    '''
    A rule that is part of a setup matrix.
    '''
    # Database fields
    id = models.AutoField(_('id'), primary_key=True)
    setupmatrix = models.ForeignKey(
        SetupMatrix, verbose_name=_('setup matrix'), related_name='rules',
        on_delete=models.CASCADE
    )
    priority = models.IntegerField(_('priority'), default=0)
    fromsetup = models.CharField(
        _('from setup'), max_length=300, blank=True, null=True,
        help_text=_("Name of the old setup (wildcard characters are supported)")
    )
    tosetup = models.CharField(
        _('to setup'), max_length=300, blank=True, null=True,
        help_text=_("Name of the new setup (wildcard characters are supported)")
    )
    cost = models.DecimalField(
        _('cost'), max_digits=20, decimal_places=8, null=True, blank=True,
        help_text=_("Cost of the conversion")
    )
    duration = models.DurationField(
        _('duration'), null=True, blank=True,
        help_text=_("Duration of the changeover")
    )

    class Manager(MultiDBManager):
        def get_by_natural_key(self, setupmatrix, priority):
            return self.get(setupmatrix=setupmatrix, priority=priority)

    def natural_key(self):
        return (self.setupmatrix, self.priority)

    objects = Manager()

    def __str__(self):
        return "%s - %s" % (
            self.setupmatrix.name if self.setupmatrix else None,
            self.priority
        )

    class Meta(AuditModel.Meta):
        ordering = ['priority']
        db_table = 'setuprule'
        unique_together = (('setupmatrix', 'priority'),)
        verbose_name = _('setup matrix rule')
        verbose_name_plural = _('setup matrix rules')


class Resource(AuditModel, HierarchyModel):
    # Database fields
    id = models.AutoField(_('id'), help_text=_('Unique identifier'), primary_key=True)

    nr = models.CharField(_('nr'), max_length=300, db_index=True, unique=True)
    name = models.CharField(_('name'), max_length=300, db_index=True)

    description = models.CharField(
        _('description'), max_length=500, null=True, blank=True
    )
    category = models.CharField(
        _('category'), max_length=300, null=True, blank=True, db_index=True
    )
    subcategory = models.CharField(
        _('subcategory'), max_length=300, null=True, blank=True, db_index=True
    )
    type = models.CharField(
        _('type'), max_length=20, null=True, blank=True, choices=enum.CommonType.to_tuple(), default='default'
    )
    maximum = models.DecimalField(
        _('maximum'), default="1.00", null=True, blank=True,
        max_digits=20, decimal_places=8,
        help_text=_('Size of the resource')
    )
    maximum_calendar = models.ForeignKey(
        Calendar, verbose_name=_('maximum calendar'), null=True, blank=True, related_name='resource_maximum_calendar',
        on_delete=models.CASCADE, help_text=_('Calendar defining the resource size varying over time')
    )
    available = models.ForeignKey(
        Calendar, verbose_name=_('available'), null=True, blank=True, related_name='resource_available',
        on_delete=models.CASCADE,
        help_text=_('Calendar defining the working hours and holidays')
    )
    location = models.ForeignKey(
        Location, verbose_name=_('location'), on_delete=models.CASCADE, related_name='resource_location', db_index=True
    )
    cost = models.DecimalField(
        _('cost'), null=True, blank=True,
        max_digits=20, decimal_places=8,
        help_text=_("Cost for using 1 unit of the resource for 1 hour"))

    efficiency = models.DecimalField(
        _('efficiency'), null=True, blank=True, max_digits=20, decimal_places=8, default=100.00,
        help_text=_("Efficiency percentage of the resource")
    )

    efficiency_calendar = models.ForeignKey(
        Calendar, verbose_name=_('efficiency calendar'), related_name='resource_efficiency_calendar',
        null=True, blank=True, on_delete=models.CASCADE,
        help_text=_('Calendar defining the efficiency percentage of the resource varying over time')
    )
    setupmatrix = models.ForeignKey(
        SetupMatrix, verbose_name=_('setupmatrix'), null=True, blank=True,
        db_index=True, on_delete=models.CASCADE, related_name='resource_setupmatrix',
        help_text=_('Setup matrix defining the conversion time and cost')
    )
    now_setup = models.CharField(
        _('now setup'), max_length=300, null=True, blank=True,
        help_text=_('Setup of the resource at the start of the plan')
    )

    # maxearly = models.DurationField(
    #     _('max early'), null=True, blank=True,
    #     help_text=_('Time window before the ask date where we look for available capacity')
    # )
    # Methods
    def __str__(self):
        return self.nr

    class Manager(MultiDBManager):
        def get_by_natural_key(self, nr):
            return self.get(nr=nr)

    natural_key = ('nr',)
    objects = Manager()

    class Meta(AuditModel.Meta):
        db_table = 'resource'
        verbose_name = _('resource')
        verbose_name_plural = _('resources')
        ordering = ['id']


class Skill(AuditModel):
    # Database fields
    id = models.AutoField(_('id'), help_text=_('Unique identifier'), primary_key=True)

    nr = models.CharField(_('nr'), max_length=300, db_index=True, unique=True)

    name = models.CharField(
        # . Translators: Translation included with Django
        _('name'), max_length=300)
    category = models.CharField(
        _('category'), max_length=300, null=True, blank=True, db_index=True
    )
    subcategory = models.CharField(
        _('subcategory'), max_length=300, null=True, blank=True, db_index=True
    )
    description = models.CharField(
        _('description'), max_length=500, null=True, blank=True
    )

    # Methods
    def __str__(self):
        return self.nr

    class Manager(MultiDBManager):
        def get_by_natural_key(self, nr):
            return self.get(nr=nr)

    natural_key = ('nr',)
    objects = Manager()

    class Meta(AuditModel.Meta):
        db_table = 'skill'
        verbose_name = _('skill')
        verbose_name_plural = _('skills')
        ordering = ['id']


class ResourceSkill(AuditModel):
    # Database fields
    id = models.AutoField(_('id'), primary_key=True)

    resource = models.ForeignKey(
        Resource, verbose_name=_('resource'), db_index=True, related_name='resourceskill_resource',
        blank=False, null=False, on_delete=models.CASCADE
    )
    skill = models.ForeignKey(
        Skill, verbose_name=_('skill'), db_index=True, related_name='resourcesskill_skill',
        blank=False, null=False, on_delete=models.CASCADE
    )
    effective_start = models.DateTimeField(
        _('effective start'), null=True, blank=True,
        help_text=_('Validity start date')
    )
    effective_end = models.DateTimeField(
        _('effective end'), null=True, blank=True,
        help_text=_('Validity end date')
    )
    priority = models.IntegerField(
        _('priority'), default=0, null=True, blank=True,
        help_text=_('Priority of this skill in a group of alternates')
    )

    class Manager(MultiDBManager):
        def get_by_natural_key(self, resource, skill):
            return self.get(resource=resource, skill=skill)

    def natural_key(self):
        return (self.resource, self.skill)

    objects = Manager()

    def __str__(self):
        return '%s - %s' % (
            self.resource.nr if self.resource else 'No resource',
            self.skill.nr if self.skill else 'No skill',
        )

    class Meta(AuditModel.Meta):
        db_table = 'resourceskill'
        unique_together = (('resource', 'skill'),)
        verbose_name = _('resource skill')
        verbose_name_plural = _('resource skills')
        ordering = ['resource', 'skill']


class OperationMaterial(AuditModel):
    # Database fields
    id = models.AutoField(_('id'), primary_key=True)
    operation = models.ForeignKey(
        Operation, verbose_name=_('operation'),
        db_index=True, related_name='operationmaterials_operation',
        blank=False, null=False, on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        Item, verbose_name=_('item'),
        db_index=True, related_name='operationmaterials_item',
        blank=False, null=False, on_delete=models.CASCADE
    )
    type = models.CharField(
        _('type'), max_length=20, null=True, blank=True, choices=enum.MaterialType.to_tuple(), default='start',
        help_text=_('Consume/produce material at the start or the end of the operationplan'),
    )
    priority = models.IntegerField(
        _('priority'), default=1, null=True, blank=True,
        help_text=_('Priority of this operation material in a group of alternates')
    )
    quantity = models.DecimalField(
        _('quantity'), default=1.00, blank=True, null=True,
        max_digits=20, decimal_places=8,
        help_text=_('Quantity to consume or produce per operationplan unit')
    )
    quantity_fixed = models.DecimalField(
        _('fixed quantity'), blank=True, null=True,
        max_digits=20, decimal_places=8,
        help_text=_('Fixed quantity to consume or produce')
    )
    materialbatch_per = models.DecimalField(
        _('materialbatch per'), blank=True, null=True,
        max_digits=20, decimal_places=8,
    )
    effective_start = models.DateTimeField(
        _('effective start'), null=True, blank=True,
        help_text=_('Validity start date')
    )
    effective_end = models.DateTimeField(
        _('effective end'), null=True, blank=True,
        help_text=_('Validity end date')
    )
    alternative_process_mode = models.CharField(
        _('alternative process mode'), max_length=20, null=True, blank=True, choices=enum.OperationMode.to_tuple())

    class Manager(MultiDBManager):
        def get_by_natural_key(self, operation, item, effective_start):
            return self.get(operation=operation, item=item, effective_start=effective_start)

    def natural_key(self):
        return (self.operation, self.item, self.effective_start)

    objects = Manager()

    def __str__(self):
        if self.effective_start:
            return '%s - %s - %s' % (
                self.operation.nr if self.operation else None,
                self.item.nr if self.item else None,
                self.effective_start
            )
        else:
            return '%s - %s' % (
                self.operation.nr if self.operation else None,
                self.item.nr if self.item else None
            )

    class Meta(AuditModel.Meta):
        db_table = 'operationmaterial'
        unique_together = (('operation', 'item', 'effective_start'),)
        verbose_name = _('operation material')
        verbose_name_plural = _('operation materials')


class OperationResource(AuditModel):
    # Database fields
    id = models.AutoField(_('identifier'), primary_key=True)
    resource = models.ForeignKey(
        Resource, verbose_name=_('resource'), db_index=True,
        related_name='operationresources',
        blank=False, null=False, on_delete=models.CASCADE
    )
    operation = models.ForeignKey(
        Operation, verbose_name=_('operation'),
        db_index=True, related_name='operationresources',
        blank=False, null=False, on_delete=models.CASCADE
    )
    quantity = models.DecimalField(
        _('quantity'), default=1.00,
        max_digits=20, decimal_places=8
    )
    priority = models.IntegerField(
        _('priority'), default=1, null=True, blank=True,
        help_text=_('Priority of this load in a group of alternates')
    )
    skill = models.ForeignKey(
        Skill, verbose_name=_('skill'), related_name='operationresources',
        null=True, blank=True, db_index=True, on_delete=models.CASCADE
    )
    setup = models.CharField(
        _('setup'), max_length=300, null=True, blank=True,
        help_text=_('Setup required on the resource for this operation')
    )
    effective_start = models.DateTimeField(
        _('effective start'), null=True, blank=True,
        help_text=_('Validity start date')
    )
    effective_end = models.DateTimeField(
        _('effective end'), null=True, blank=True,
        help_text=_('Validity end date')
    )
    alternative_process_mode = models.CharField(
        _('alternative process mode'), max_length=20, null=True, blank=True, choices=enum.OperationMode.to_tuple())

    # name = models.CharField(
    #     # . Translators: Translation included with Django
    #     _('name'), max_length=300, null=True, blank=True,
    #     help_text=_('Optional name of this load')
    # )
    # search = models.CharField(
    #     _('search mode'), max_length=20,
    #     null=True, blank=True, choices=searchmode,
    #     help_text=_('Method to select preferred alternate')
    # )

    class Manager(MultiDBManager):
        def get_by_natural_key(self, operation, resource, skill, effective_start):
            return self.get(operation=operation, resource=resource, skill=skill, effective_start=effective_start)

    def natural_key(self):
        return (self.operation, self.resource, self.skill, self.effective_start)

    objects = Manager()

    def __str__(self):
        if self.effective_start:
            return '%s - %s - %s - %s' % (
                self.operation.nr if self.operation else None,
                self.resource.nr if self.resource else None,
                self.skill.nr if self.skill else None,
                self.effective_start
            )
        else:
            return '%s - %s - %s' % (
                self.operation.nr if self.operation else None,
                self.resource.nr if self.resource else None,
                self.skill.nr if self.skill else None
            )

    class Meta(AuditModel.Meta):
        db_table = 'operationresource'
        unique_together = (('operation', 'resource', 'skill', 'effective_start'),)
        verbose_name = _('operation resource')
        verbose_name_plural = _('operation resources')


class Supplier(AuditModel, HierarchyModel):
    # Database fields
    # 设置外键显示的值
    display_key = 'nr'
    # 设置外键导入的值
    foreign_input_key = 'nr'
    # 设置owner显示的值
    # owner_display_key = 'nr'
    # 添加自增列
    id = models.AutoField(_('id'), help_text=_('Unique identifier'), primary_key=True)
    nr = models.CharField(_('supplier nr'), max_length=300, db_index=True, unique=True)
    # 设置name为非主键
    name = models.CharField(_('name'), max_length=300, primary_key=False, db_index=True)
    area = models.CharField(_('area'), max_length=300, db_index=True, null=True, blank=True)
    address = models.CharField(_('address'), max_length=300, db_index=True, null=True, blank=True)
    ship_address = models.CharField(_('ship address'), max_length=300, db_index=True, null=True, blank=True)
    country = models.CharField(_('country'), max_length=300, db_index=True, null=True, blank=True)
    city = models.CharField(_('city'), max_length=300, db_index=True, null=True, blank=True)
    phone = models.CharField(_('phone'), max_length=300, db_index=True, null=True, blank=True)
    telephone = models.CharField(_('telephone'), max_length=300, db_index=True, null=True, blank=True)
    contact = models.CharField(_('contact'), max_length=300, db_index=True, null=True, blank=True)
    email = models.CharField(_('email'), max_length=300, db_index=True, null=True, blank=True)
    available = models.ForeignKey(
        Calendar, verbose_name=_('available'),
        null=True, blank=True, on_delete=models.CASCADE,
        help_text=_('Calendar defining the working hours and holidays')
    )
    description = models.CharField(_('description'), max_length=500, null=True, blank=True)
    category = models.CharField(_('category'), max_length=300, null=True, blank=True, db_index=True)
    subcategory = models.CharField(_('subcategory'), max_length=300, null=True, blank=True, db_index=True)

    def __str__(self):
        return self.name

    # CMARK 上传时,使用以下判断是否可以使用
    class Manager(MultiDBManager):
        def get_by_natural_key(self, nr):
            return self.get(nr=nr)

    # CMARK 定义自然key, 在创建/编辑的过程中, 可以使用这个键来做查询
    # 　比如上传时，id(主键)是非必须的，所有通过natural_key 查询, 如果填写了id就使用id做查询
    natural_key = ('nr',)

    # 设置manager 这个要和get_by_natural_key一起使用!
    objects = Manager()

    class Meta(AuditModel.Meta):
        db_table = 'supplier'
        verbose_name = _('supplier')
        verbose_name_plural = _('suppliers')
        ordering = ['id']


class ItemSupplier(AuditModel):
    # Database fields
    # 设置外键显示的值
    display_key = 'nr'
    # 设置外键导入的值
    foreign_input_key = 'nr'
    id = models.AutoField(_('identifier'), primary_key=True)
    item = models.ForeignKey(
        Item, verbose_name=_('item'),
        db_index=True, related_name='itemsuppliers',
        null=False, blank=False, on_delete=models.CASCADE
    )
    supplier = models.ForeignKey(
        Supplier, verbose_name=_('supplier'),
        db_index=True, related_name='suppliers',
        null=False, blank=False, on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location, verbose_name=_('location'),
        db_index=True, related_name='itemsupplier_location',
        null=False, blank=False, on_delete=models.CASCADE
    )
    supplier_item_nr = models.CharField(_('supplier item nr'), max_length=300, db_index=True, null=True, blank=True)
    status = models.CharField(_('status'), max_length=20, choices=enum.RmStatus.to_tuple())
    cost = models.DecimalField(_('cost'), max_digits=20, decimal_places=8)
    monetary_unit = models.CharField(_('monetary unit'), max_length=20)
    cost_unit = models.DecimalField(_('cost unit'), max_digits=20, decimal_places=8)
    priority = models.IntegerField(_('priority'), default=0, help_text=_('Priority among all alternates'))
    ratio = models.DecimalField(_('ratio'), max_digits=20, decimal_places=8, default=100, null=True, blank=True)
    moq = models.DecimalField(_('MOQ'), max_digits=20, decimal_places=8)
    order_unit_qty = models.DecimalField(_('order unit qty'), max_digits=20, decimal_places=8, default=0)
    order_max_qty = models.DecimalField(_('order max qty'), max_digits=20, decimal_places=8, default=0)
    product_time = models.DecimalField(_('product time'), max_digits=20, decimal_places=8, default=0, null=True,
                                       blank=True)
    load_time = models.DecimalField(_('load time'), null=True, max_digits=20, decimal_places=8, default=0,
                                    blank=True)
    transit_time = models.DecimalField(_('transit time'), max_digits=20, decimal_places=8, default=0, null=True,
                                       blank=True)
    receive_time = models.DecimalField(_('receive time'), max_digits=20, decimal_places=8, default=0, null=True,
                                       blank=True)
    mpq = models.DecimalField(_('mpq'), max_digits=20, decimal_places=8, null=True, blank=True)
    earliest_order_date = models.DateField(_('earliest order date'), null=True, blank=True)
    plan_supplier_date = models.DateField(_('plan supplier date'), null=True, blank=True)
    plan_load_date = models.DateField(_('plan load date'), null=True, blank=True)
    plan_receive_date = models.DateField(_('plan receive date'), null=True, blank=True)
    outer_package_num = models.IntegerField(_('outer package num'), null=True, blank=True)
    pallet_num = models.IntegerField(_('pallet num'), null=True, blank=True)
    outer_package_gross_weight = models.DecimalField(_('outer package gross weight'), max_digits=20, decimal_places=8,
                                                     null=True, blank=True)
    pallet_gross_weight = models.DecimalField(_('pallet gross weight'), max_digits=20, decimal_places=8,
                                              null=True, blank=True)
    outer_package_volume = models.DecimalField(_('outer package volume'), max_digits=20, decimal_places=8,
                                               null=True, blank=True)
    pallet_volume = models.DecimalField(_('pallet volume'), max_digits=20, decimal_places=8, null=True, blank=True)
    plan_list_date = models.DateField(_('plan list date'), null=True, blank=True)
    plan_delist_date = models.DateField(_('plan delist date'), null=True, blank=True)
    origin_country = models.CharField(_('origin country'), max_length=300, null=True, blank=True)
    effective_start = models.DateTimeField(
        _('effective start'), null=True, blank=True,
        help_text=_('Validity start date')
    )
    effective_end = models.DateTimeField(
        _('effective end'), null=True, blank=True,
        help_text=_('Validity end date')
    )
    description = models.CharField(_('description'), max_length=500, null=True, blank=True)

    class Manager(MultiDBManager):
        def get_by_natural_key(self, item, supplier):
            return self.get(item=item, supplier=supplier)

    def natural_key(self):
        return self.item, self.supplier

    objects = Manager()

    def __str__(self):
        return '%s - %s' % (
            self.supplier.nr if self.supplier else 'No supplier',
            self.item.nr if self.item else 'No item',
        )

    class Meta(AuditModel.Meta):
        db_table = 'itemsupplier'
        unique_together = (('item', 'supplier'),)
        verbose_name = _('item supplier')
        verbose_name_plural = _('item suppliers')

    def wd2cd(self):
        calendar = self.supplier.available
        return Calendar.cd(calendar, datetime.now().date(), self.total_wds())

    def total_wds(self):
        return reduce(lambda x, y: x + y, map(lambda x: x if x else 0,
                                              [self.product_time, self.load_time, self.transit_time,
                                               self.receive_time]))


class ItemDistribution(AuditModel):
    # Database fields
    id = models.AutoField(_('id'), primary_key=True)
    item = models.ForeignKey(
        Item, verbose_name=_('item'),
        db_index=True, related_name='itemdistributions_item',
        null=False, blank=False, on_delete=models.CASCADE
    )
    origin = models.ForeignKey(
        Location, verbose_name=_('origin'), on_delete=models.CASCADE,
        db_index=True, related_name='itemdistributions_origin'
    )
    destination = models.ForeignKey(
        Location, verbose_name=_('destination'),
        db_index=True, related_name='itemdistributions_destination',
        on_delete=models.CASCADE
    )
    cost = models.DecimalField(
        _('cost'), max_digits=20, decimal_places=8, help_text=_("Shipping cost per unit"))
    load_time = models.DecimalField(
        _('load time'), null=True, blank=True,
        max_digits=20, decimal_places=8, default=0
    )
    transit_time = models.DecimalField(
        _('transit time'), null=True, blank=True,
        max_digits=20, decimal_places=8, default=0
    )
    receive_time = models.DecimalField(
        _('receive time'), null=True, blank=True,
        max_digits=20, decimal_places=8, default=0
    )
    size_minimum = models.DecimalField(
        _('size minimum'), null=True, blank=True,
        max_digits=20, decimal_places=8, default=1
    )
    size_multiple = models.DecimalField(
        _('size multiple'), null=True, blank=True,
        max_digits=20, decimal_places=8, default=0
    )
    priority = models.IntegerField(
        _('priority'), default=1, null=True, blank=True,
        help_text=_('Priority among all alternates')
    )
    resource = models.ForeignKey(
        Resource, verbose_name=_('resource'), null=True, blank=True,
        db_index=True, related_name='itemdistributions_resource', on_delete=models.CASCADE,
        help_text=_("Resource to model the distribution capacity")
    )
    resource_qty = models.DecimalField(
        _('resource quantity'), null=True, blank=True,
        max_digits=20, decimal_places=8, default=1.0,
        help_text=_("Resource capacity consumed per distributed unit")
    )
    effective_start = models.DateTimeField(
        _('effective start'), null=True, blank=True,
        help_text=_('Validity start date')
    )
    effective_end = models.DateTimeField(
        _('effective end'), null=True, blank=True,
        help_text=_('Validity end date'))

    class Manager(MultiDBManager):
        def get_by_natural_key(self, item, origin, destination, resource):
            return self.get(item=item, origin=origin, destination=destination, resource=resource)

    def natural_key(self):
        return (self.item, self.origin, self.destination, self.resource)

    objects = Manager()

    def __str__(self):
        return '%s - %s - %s - %s' % (
            self.item.nr if self.item else 'No item',
            self.origin.nr if self.origin else 'No origin',
            self.destination.nr if self.destination else 'Any destination',
            self.resource.nr if self.resource else 'No resource')

    class Meta(AuditModel.Meta):
        db_table = 'itemdistribution'
        unique_together = (('item', 'origin', 'destination', 'resource'),)
        verbose_name = _('item distribution')
        verbose_name_plural = _('item distributions')


class ForecastYear(AuditModel):
    date_types = (
        ('W', _('W')),
        ('M', _('M')),
    )

    id = models.AutoField(_('id'), help_text=_('Unique identifier'), primary_key=True)
    item = models.ForeignKey(
        Item, verbose_name=_('item'),
        db_index=True, related_name='forecastyear_item',
        null=False, blank=False, on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location, verbose_name=_('location'),
        db_index=True, related_name='forecastyear_locatoin',
        null=False, blank=False, on_delete=models.CASCADE
    )
    customer = models.ForeignKey(
        Customer, verbose_name=_('customer'),
        db_index=True, related_name='forecastyear_customer',
        null=True, blank=True, on_delete=models.CASCADE
    )
    year = models.IntegerField(_('year'), db_index=True)
    date_number = models.IntegerField(_('date_number'), db_index=True)

    date_type = models.CharField(
        _('date_type'), max_length=20, choices=enum.ForecastDateType.to_tuple(), default='W', null=True, blank=True)

    ratio = models.DecimalField(_('forecast ratio'), max_digits=20, decimal_places=8, default=100, null=False,
                                blank=True)
    normal_qty = models.DecimalField(_('normal qty'), max_digits=20, decimal_places=8, null=False, default=0)
    new_product_plan_qty = models.DecimalField(_('new product plan qty'), max_digits=20, decimal_places=8, null=False,
                                               blank=True, default=0)
    promotion_qty = models.DecimalField(_('promotion qty'), max_digits=20, decimal_places=8, null=False,
                                        blank=True, default=0)
    # 解析过的时间, 通过 date type + date number
    parsed_date = models.DateTimeField(_('parsed_date'), editable=False, db_index=True, default=timezone.now)

    class Manager(MultiDBManager):
        # 批量创建复写
        def bulk_create(self, objs, batch_size=None):
            for o in objs:
                o.set_parsed_date()
            super(ForecastYear.Manager, self).bulk_create(objs, batch_size)

    def set_parsed_date(self):
        self.parsed_date = Forecast.parse_date(self.date_type, self.year, self.date_number)

    objects = Manager()

    class Meta(AuditModel.Meta):
        db_table = 'forecast_year'
        unique_together = (('item', 'location', 'customer', 'year', 'date_type', 'date_number'),)
        verbose_name = _('forecast_year')
        verbose_name_plural = _('forecast_years')

    def save(self, *args, **kwargs):
        # 解析方法
        # Call the real save() method
        self.set_parsed_date()
        super(ForecastYear, self).save(*args, **kwargs)


class ForecastCommentOperation:
    statuses = (
        ('init', _('forecast init')),
        ('ok', _('forecast ok')),
        ('nok', _('forecast nok')),
        ('cancel', _('forecast cancel')),
        ('release', _('forecast release')),
        ('confirm', _('forecast confirm')),
    )

    can_ok_status = ('init', 'nok', 'cancel')
    can_nok_status = ('init', 'ok')
    can_cancel_status = ('init', 'nok', 'ok')
    can_release_status = ('ok')

    # 报表状态
    compare_report_status = ('init', 'nok', 'ok', 'release', 'confirm',)

    def can_ok(self):
        return self.status in self.can_ok_status

    def can_nok(self):
        return self.status in self.can_nok_status

    def can_cancel(self):
        return self.status in self.can_cancel_status

    def can_release(self):
        return self.status in self.can_release_status


class ForecastVersion(AuditModel, ForecastCommentOperation):
    nr = models.CharField(_('nr'), max_length=300, editable=False, db_index=True,
                          primary_key=True)
    status = models.CharField(_('status'), max_length=20, choices=enum.ForecastCommentStatus.to_tuple(), default='init')
    create_user = models.ForeignKey(
        User, verbose_name=_('create_user'),
        db_index=True, related_name='forecastversion_create_user',
        null=False, blank=False, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.nr

    class Meta(AuditModel.Meta):
        db_table = 'forecast_version'
        verbose_name = _('forecast_version')
        verbose_name_plural = _('forecast_versions')

    # comment
    comments = GenericRelation(Comment, verbose_name='forecastversion comment', related_name='forecast_version_comment',
                               object_id_field='object_pk',
                               on_delete=models.CASCADE)


class Forecast(AuditModel, ForecastCommentOperation):
    id = models.AutoField(_('id'), help_text=_('Unique identifier'), primary_key=True)

    item = models.ForeignKey(
        Item, verbose_name=_('item'),
        db_index=True, related_name='forecast_item',
        null=False, blank=False, on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location, verbose_name=_('location'),
        db_index=True, related_name='forecast_location',
        null=False, blank=False, on_delete=models.CASCADE
    )
    customer = models.ForeignKey(
        Customer, verbose_name=_('customer'),
        db_index=True, related_name='forecast_customer',
        null=True, blank=True, on_delete=models.CASCADE
    )
    year = models.IntegerField(_('year'), db_index=True)
    date_number = models.IntegerField(_('date_number'), db_index=True)

    date_type = models.CharField(
        _('date_type'), max_length=20, choices=enum.ForecastDateType.to_tuple(), default='W')
    priority = models.IntegerField(
        _('priority'), default=0,
        help_text=_('Priority of the demand (lower numbers indicate more important demands)')
    )
    ratio = models.DecimalField(_('forecast ratio'), max_digits=20, decimal_places=8, default=100)
    normal_qty = models.DecimalField(_('normal qty'), max_digits=20, decimal_places=8, default=0)
    new_product_plan_qty = models.DecimalField(_('new product plan qty'), max_digits=20, decimal_places=8, default=0)
    promotion_qty = models.DecimalField(_('promotion qty'), max_digits=20, decimal_places=8, default=0)
    status = models.CharField(_('status'), max_length=20, choices=enum.ForecastCommentStatus.to_tuple(), default='init')
    create_user = models.ForeignKey(
        User, verbose_name=_('create_user'),
        db_index=True, related_name='forecast_create_user',
        null=False, blank=False, on_delete=models.CASCADE
    )
    version = models.ForeignKey(ForecastVersion, verbose_name=_('forecast version'),
                                db_index=True, related_name='forecast_version', on_delete=models.CASCADE)

    # 解析过的时间, 通过 date_type + date number
    parsed_date = models.DateTimeField(_('parsed_date'), editable=False, db_index=True, default=timezone.now)

    # comment
    comments = GenericRelation(Comment, verbose_name='forecast comment', related_name='forecast_comment',
                               object_id_field='object_pk',
                               on_delete=models.CASCADE)

    @classmethod
    def parse_date(cls, date_type, year, date_number):
        if date_type == 'W':
            return la_time.weeknum2dt(year, date_number)
        elif date_type == 'M':
            return la_time.monthnum2dt(year, date_number)
        else:
            raise Exception('Error datetype in forecast')

    class Manager(MultiDBManager):
        # def get_by_natural_key(self, item, location, customer,year,date_type,date_number,version_id):
        #     return self.get(item=item, location=location, customer=customer,year=year,date_type=date_type,date_number=date_number,version_id=version_id)

        # 批量创建复写
        def bulk_create(self, objs, batch_size=None):
            for o in objs:
                o.set_parsed_date()
            super(Forecast.Manager, self).bulk_create(objs, batch_size)

    # def natural_key(self):
    #     return (self.item, self.location, self.customer,self.year,self.date_type,self.date_number,self.version_id)

    def set_parsed_date(self):
        self.parsed_date = Forecast.parse_date(self.date_type, self.year, self.date_number)

    objects = Manager()

    # def __str__(self):
    #     return '%s - %s - %s' % (
    #         self.item.nr, self.location.nr, self.customer.nr)

    class Meta(AuditModel.Meta):
        db_table = 'forecast'
        unique_together = (('item', 'location', 'customer', 'year', 'date_type', 'date_number', 'version'),)
        verbose_name = _('forecast')
        verbose_name_plural = _('forecasts')

    def save(self, *args, **kwargs):
        # 解析方法
        # Call the real save() method
        self.set_parsed_date()
        super(Forecast, self).save(*args, **kwargs)


class Demand(AuditModel, HierarchyModel):
    # Status
    demandstatus = (
        ('inquiry', _('inquiry')),
        ('quote', _('quote')),
        ('open', _('open')),
        ('closed', _('closed')),
        ('canceled', _('canceled')),
    )

    # Database fields
    description = models.CharField(
        _('description'), max_length=500, null=True, blank=True
    )
    category = models.CharField(
        _('category'), max_length=300, null=True, blank=True, db_index=True
    )
    subcategory = models.CharField(
        _('subcategory'), max_length=300, null=True, blank=True, db_index=True
    )
    customer = models.ForeignKey(
        Customer, verbose_name=_('customer'),
        db_index=True, on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        Item, verbose_name=_('item'), db_index=True, on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location, verbose_name=_('location'),
        db_index=True, on_delete=models.CASCADE
    )
    due = models.DateTimeField(_('due'), help_text=_('Due date of the demand'), db_index=True)
    status = models.CharField(
        _('status'), max_length=10, null=True, blank=True,
        choices=demandstatus, default='open',
        help_text=_('Status of the demand. Only "open" demands are planned'),
    )
    operation = models.ForeignKey(
        Operation,
        verbose_name=_('delivery operation'), null=True, blank=True,
        related_name='used_demand', on_delete=models.CASCADE,
        help_text=_('Operation used to satisfy this demand')
    )
    quantity = models.DecimalField(
        _('quantity'), max_digits=20, decimal_places=8, default=1
    )
    priority = models.IntegerField(
        _('priority'), default=10,
        help_text=_('Priority of the demand (lower numbers indicate more important demands)')
    )
    minshipment = models.DecimalField(
        _('minimum shipment'), null=True, blank=True,
        max_digits=20, decimal_places=8,
        help_text=_('Minimum shipment quantity when planning this demand')
    )
    maxlateness = models.DurationField(
        _('maximum lateness'), null=True, blank=True,
        help_text=_("Maximum lateness allowed when planning this demand")
    )
    delay = models.DurationField(
        _('delay'), null=True, blank=True, editable=False
    )
    plannedquantity = models.DecimalField(
        _('planned quantity'), max_digits=20, decimal_places=8, null=True, blank=True, editable=False,
        help_text=_('Quantity planned for delivery')
    )
    deliverydate = models.DateTimeField(
        _('delivery date'), help_text=_('Delivery date of the demand'), null=True, blank=True, editable=False,
    )
    plan = JSONBField(default="{}", null=True, blank=True, editable=False)

    # Convenience methods
    def __str__(self):
        return self.name

    class Meta(AuditModel.Meta):
        db_table = 'demand'
        verbose_name = _('sales order')
        verbose_name_plural = _('sales orders')
        ordering = ['name']


class SalesOrder(AuditModel):
    id = models.AutoField(_('id'), help_text=_('Unique identifier'), primary_key=True)
    nr = models.CharField(_('nr'), max_length=300, db_index=True, unique=True, null=True, blank=True)
    location = models.ForeignKey(
        Location, verbose_name=_('location'),
        db_index=True, related_name='salesorder_location',
        null=False, blank=False, on_delete=models.CASCADE)
    customer = models.ForeignKey(
        Customer, verbose_name=_('customer'),
        db_index=True, related_name='salesorder_customer',
        null=True, blank=True, on_delete=models.CASCADE)
    status = models.CharField(_('status'), max_length=20, null=True, blank=True,
                              choices=enum.SalesOrderStatus.to_tuple())
    max_lateness = models.DecimalField(_('max lateness'), max_digits=20, decimal_places=8, null=True, blank=True)
    min_shipment = models.DecimalField(_('min shipment'), max_digits=20, decimal_places=8, null=True, blank=True)

    def __str__(self):
        return self.id

    class Meta(AuditModel.Meta):
        db_table = 'salesorder'
        verbose_name = _('sales order')
        verbose_name_plural = _('sales orders')
        ordering = ['id']


class SalesOrderItem(AuditModel):
    id = models.AutoField(_('id'), primary_key=True)
    line_no = models.CharField(_('line no'), max_length=300, null=True, blank=True)
    sales_order = models.ForeignKey(
        SalesOrder, verbose_name=_('sales order'),
        db_index=True, related_name='salesorderitem_saleorder',
        null=True, blank=True, on_delete=models.CASCADE)
    item = models.ForeignKey(
        Item, verbose_name=_('item'),
        db_index=True, related_name='salesorderitem_item',
        null=False, blank=False, on_delete=models.CASCADE)
    qty = models.DecimalField(_('qty'), max_digits=20, null=True, blank=True, decimal_places=8)
    schedule_qty = models.DecimalField(_('schedule qty'), max_digits=20, null=True, blank=True, decimal_places=8)
    deliver_qty = models.DecimalField(_('deliver qty'), max_digits=20, null=True, blank=True, decimal_places=8)
    due = models.DateTimeField(_('due'), null=True, blank=True, db_index=True)
    priority = models.IntegerField(_('priority'), default=0, blank=True, null=True)
    status = models.CharField(_('status'), max_length=20, null=True, blank=True,
                              choices=enum.SalesOrderStatus.to_tuple())
    max_lateness = models.DecimalField(_('max lateness'), max_digits=20, null=True, blank=True, decimal_places=8)
    min_shipment = models.DecimalField(_('min shipment'), max_digits=20, null=True, blank=True, decimal_places=8)

    def __str__(self):
        return self.id

    class Meta(AuditModel.Meta):
        db_table = 'sales_order_item'
        verbose_name = _('sales order item')
        verbose_name_plural = _('sales orders items')
        ordering = ['id']


class OperationPlan(AuditModel):
    # Possible types
    types = (
        ('STCK', _('inventory')),
        ('MO', _('manufacturing order')),
        ('PO', _('purchase order')),
        ('DO', _('distribution order')),
        ('DLVR', _('delivery order')),
    )

    # Possible status
    orderstatus = (
        ('proposed', _('proposed')),
        ('approved', _('approved')),
        ('confirmed', _('confirmed')),
        ('closed', _('closed')),
    )

    # Database fields
    # Common fields
    id = models.AutoField(
        _('identifier'), primary_key=True,
        help_text=_('Unique identifier of an operationplan')
    )
    status = models.CharField(
        _('status'), null=True, blank=True, max_length=20, choices=orderstatus,
        help_text=_('Status of the order')
    )
    type = models.CharField(
        _('type'), max_length=5, choices=types, default='MO',
        help_text=_('Order type'), db_index=True
    )
    reference = models.CharField(
        _('reference'), max_length=300, null=True, blank=True,
        help_text=_('External reference of this order')
    )
    quantity = models.DecimalField(
        _('quantity'), max_digits=20,
        decimal_places=8, default=1.00
    )
    color = models.DecimalField(
        _('color'), max_digits=20, null=True, blank=True,
        decimal_places=8, default=0
    )
    startdate = models.DateTimeField(
        _('start date'), help_text=_('start date'),
        null=True, blank=True, db_index=True
    )
    enddate = models.DateTimeField(
        _('end date'), help_text=_('end date'),
        null=True, blank=True, db_index=True
    )
    criticality = models.DecimalField(
        _('criticality'), max_digits=20,
        decimal_places=8, null=True, blank=True, editable=False
    )
    delay = models.DurationField(
        _('delay'), null=True, blank=True, editable=False
    )
    plan = JSONBField(default="{}", null=True, blank=True, editable=False)
    # Used only for manufacturing orders
    operation = models.ForeignKey(
        Operation, verbose_name=_('operation'), related_name='operationplan_operation',
        db_index=True, null=True, blank=True, on_delete=models.CASCADE
    )
    owner = models.ForeignKey(
        'self', verbose_name=_('owner'), null=True, blank=True,
        related_name='xchildren', help_text=_('Hierarchical parent'),
        on_delete=models.CASCADE
    )
    # Used for purchase orders and distribution orders
    item = models.ForeignKey(
        Item, verbose_name=_('item'), on_delete=models.CASCADE,
        null=True, blank=True, db_index=True
    )
    # Used only for distribution orders
    origin = models.ForeignKey(
        Location, verbose_name=_('origin'), null=True, blank=True,
        related_name='origins', db_index=True, on_delete=models.CASCADE
    )
    destination = models.ForeignKey(
        Location, verbose_name=_('destination'), on_delete=models.CASCADE,
        null=True, blank=True, related_name='destinations', db_index=True
    )
    # Used only for purchase orders
    supplier = models.ForeignKey(
        Supplier, verbose_name=_('supplier'),
        null=True, blank=True, db_index=True, on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location, verbose_name=_('location'),
        null=True, blank=True, db_index=True, on_delete=models.CASCADE
    )
    # Used for delivery operationplans
    demand = models.ForeignKey(
        Demand, verbose_name=_('demand'),
        null=True, blank=True, db_index=True, on_delete=models.CASCADE
    )
    due = models.DateTimeField(
        _('due'), help_text=_('Due date of the demand/forecast'),
        null=True, blank=True, editable=False
    )
    name = models.CharField(
        _('name'), max_length=1000, null=True,
        blank=True, db_index=True
    )

    class Manager(MultiDBManager):
        def get_by_natural_key(self, reference):
            # Note: we are not enforcing the uniqueness of this natural key in the database
            return self.get(reference=reference)

    def natural_key(self):
        return (self.reference)

    objects = Manager()

    natural_key = ('reference',)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if not self.id:
            if 'using' in kwargs:
                db = kwargs['using']
            else:
                state = getattr(self, '_state', None)
                db = state.db if state else DEFAULT_DB_ALIAS
            self.id = OperationPlan.objects.all().using(db).aggregate(Max('id'))['id__max']
            if self.id:
                self.id += 1
            else:
                self.id = 1
            kwargs['force_insert'] = True

        # Call the real save() method
        super(OperationPlan, self).save(*args, **kwargs)

    class Meta(AuditModel.Meta):
        db_table = 'operationplan'
        verbose_name = _('operationplan')
        verbose_name_plural = _('operationplans')
        ordering = ['id']


class OperationPlanResource(AuditModel):
    # Possible status
    OPRstatus = (
        ('proposed', _('proposed')),
        ('confirmed', _('confirmed')),
    )

    # Database fields
    resource = models.ForeignKey(
        Resource, verbose_name=_('resource'), db_index=True,
        related_name="operationplanresources", on_delete=models.CASCADE
    )
    operationplan = models.ForeignKey(
        OperationPlan, verbose_name=_('operationplan'), db_index=True,
        related_name="resources", on_delete=models.CASCADE
    )
    quantity = models.DecimalField(_('quantity'), max_digits=20, decimal_places=8)
    startdate = models.DateTimeField(_('startdate'), db_index=True)
    enddate = models.DateTimeField(_('enddate'), db_index=True)
    setup = models.CharField(_('setup'), max_length=300, null=True)
    status = models.CharField(
        _('status'), null=True, blank=True, max_length=20, choices=OPRstatus,
        help_text=_('Status of the OperationPlanResource')
    )

    class Manager(MultiDBManager):
        def get_by_natural_key(self, operationplan, resource):
            # Note: we are not enforcing the uniqueness of this natural key in the database
            return self.get(operationplan=operationplan, resource=resource)

    def natural_key(self):
        return (self.operationplan, self.resource)

    objects = Manager()

    def __str__(self):
        return "%s %s %s %s" % (self.resource, self.startdate, self.enddate, self.status)

    natural_key = ('operationplan', 'resource')

    class Meta:
        db_table = 'operationplanresource'
        ordering = ['resource', 'startdate']
        verbose_name = _('operationplan resource')
        verbose_name_plural = _('operationplan resources')


class OperationPlanMaterial(AuditModel):
    # Possible status
    OPMstatus = (
        ('proposed', _('proposed')),
        ('confirmed', _('confirmed')),
    )

    # Database fields
    item = models.ForeignKey(
        Item, verbose_name=_('item'), related_name='operationplanmaterials',
        null=True, blank=True, db_index=True, on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location, verbose_name=_('location'), null=True, blank=True,
        related_name='operationplanmaterials', db_index=True,
        on_delete=models.CASCADE
    )
    operationplan = models.ForeignKey(
        OperationPlan, verbose_name=_('operationplan'), db_index=True,
        related_name="materials", on_delete=models.CASCADE
    )
    quantity = models.DecimalField(_('quantity'), max_digits=20, decimal_places=8)
    flowdate = models.DateTimeField(_('date'), db_index=True)
    onhand = models.DecimalField(_('onhand'), max_digits=20, decimal_places=8, null=True, blank=True)
    minimum = models.DecimalField(_('minimum'), max_digits=20, decimal_places=8, null=True, blank=True)
    periodofcover = models.DecimalField(_('periodofcover'), max_digits=20, decimal_places=8, null=True, blank=True)
    status = models.CharField(
        _('status'), null=True, blank=True, max_length=20, choices=OPMstatus,
        help_text=_('Status of the OperationPlanMaterial')
    )

    class Manager(MultiDBManager):
        def get_by_natural_key(self, operationplan, item, location):
            # Note: we are not enforcing the uniqueness of this natural key in the database
            return self.get(operationplan=operationplan, item=item, location=location)

    def natural_key(self):
        return (self.operationplan, self.item, self.location)

    objects = Manager()

    def __str__(self):
        return "%s @ %s %s %s %s" % (self.item_id, self.location_id, self.flowdate, self.quantity, self.status)

    natural_key = ('operationplan', 'item', 'location')

    class Meta:
        db_table = 'operationplanmaterial'
        ordering = ['item', 'location', 'flowdate']
        verbose_name = _('operationplan material')
        verbose_name_plural = _('operationplan materials')


class DistributionOrder(OperationPlan):
    shipping_date = AliasDateTimeField(db_column='startdate', verbose_name=_('shipping date'), null=True, blank=True)
    receipt_date = AliasDateTimeField(db_column='enddate', verbose_name=_('receipt date'), null=True, blank=True)

    class DistributionOrderManager(OperationPlan.Manager):
        def get_queryset(self):
            return super(DistributionOrder.DistributionOrderManager, self).get_queryset() \
                .filter(type='DO')
            # .defer("operation", "owner", "supplier", "location")

    objects = DistributionOrderManager()

    def save(self, *args, **kwargs):
        self.type = 'DO'
        self.operation = self.owner = self.location = self.supplier = None
        super(DistributionOrder, self).save(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = _('distribution order')
        verbose_name_plural = _('distribution orders')


class PurchaseOrder(OperationPlan):
    ordering_date = AliasDateTimeField(db_column='startdate', verbose_name=_('ordering date'), null=True, blank=True)
    receipt_date = AliasDateTimeField(db_column='enddate', verbose_name=_('receipt date'), null=True, blank=True)

    class PurchaseOrderManager(OperationPlan.Manager):
        def get_queryset(self):
            return super(PurchaseOrder.PurchaseOrderManager, self).get_queryset() \
                .filter(type='PO')
            # Note: defer screws up the model name when deleting a PO
            # .defer("operation", "owner", "origin", "destination")

    objects = PurchaseOrderManager()

    def save(self, *args, **kwargs):
        self.type = 'PO'
        self.operation = self.owner = self.origin = self.destination = None
        super(PurchaseOrder, self).save(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = _('purchase order')
        verbose_name_plural = _('purchase orders')


class ManufacturingOrder(OperationPlan):
    class ManufacturingOrderManager(OperationPlan.Manager):
        def get_queryset(self):
            return super(ManufacturingOrder.ManufacturingOrderManager, self).get_queryset() \
                .filter(type='MO')
            # Note: defer screws up the model name when deleting a PO
            # .defer("supplier", "location", "origin", "destination")

    objects = ManufacturingOrderManager()

    def save(self, *args, **kwargs):
        self.type = 'MO'
        self.supplier = self.origin = self.destination = None
        if self.operation:
            self.item = self.operation.item
            self.location = self.operation.location
        super(ManufacturingOrder, self).save(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = _('manufacturing order')
        verbose_name_plural = _('manufacturing orders')


class DeliveryOrder(OperationPlan):
    class DeliveryOrderManager(OperationPlan.Manager):
        def get_queryset(self):
            return super(DeliveryOrder.DeliveryOrderManager, self).get_queryset() \
                .filter(demand__isnull=False, owner__isnull=True)
            # Note: defer screws up the model name when deleting a PO
            # .defer("operation", "owner", "supplier", "location", "origin", "destination")

    objects = DeliveryOrderManager()

    def save(self, *args, **kwargs):
        self.type = 'DLVR'
        self.supplier = self.origin = self.destination = self.operation = self.owner = None
        if self.demand:
            self.item = self.demand.item
            self.location = self.demand.location
        super(DeliveryOrder, self).save(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = _('delivery order')
        verbose_name_plural = _('delivery orders')
