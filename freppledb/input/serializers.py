#
# Copyright (C) 2015 by frePPLe bvba
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

from freppledb.common.api.views import frePPleListAPIView, frePPleListCreateAPIView, frePPleRetrieveUpdateDestroyAPIView
import freppledb.input.models

from rest_framework_bulk.drf3.serializers import BulkListSerializer, BulkSerializerMixin
from django_filters import rest_framework as filters
from freppledb.common.api.serializers import ModelSerializer, CustomerNumberPagination
from django.utils.translation import ugettext_lazy as _
import django_filters
from rest_framework import serializers


class CalendarFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.Calendar
        fields = {'name': ['exact', 'in', 'contains', ],
                  'description': ['exact', 'contains', ],
                  'category': ['exact', 'contains', ],
                  'subcategory': ['exact', 'contains', ],
                  'defaultvalue': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'source': ['exact', 'in', ],
                  }
        filter_fields = (
            'name', 'description', 'category', 'subcategory', 'defaultvalue', 'source', 'created_at', 'updated_at')


class CalendarSerializer(BulkSerializerMixin, ModelSerializer):
    name = serializers.CharField(read_only=False)

    class Meta:
        model = freppledb.input.models.Calendar
        # fields = ('name', 'description', 'category', 'subcategory', 'defaultvalue', 'source', 'lastmodified')
        # fields该序列化器包含模型类中的哪些字段，'__all__'为包含所有字段
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'name'
        partial = True


class CalendarAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.Calendar.objects.all()
    serializer_class = CalendarSerializer
    filter_class = CalendarFilter
    ordering_fields = ('id')


class CalendardetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.Calendar.objects.all()
    serializer_class = CalendarSerializer


class CalendarBucketFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.CalendarBucket
        fields = {'id': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'calendar': ['exact', 'in', ],
                  'value': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'priority': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'startdate': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'enddate': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'endtime': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'source': ['exact', 'in', ],
                  }

        filter_fields = (
            'id', 'calendar', 'value', 'priority', 'source', 'enddate', 'endtime', 'created_at', 'updated_at')


class CalendarBucketSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = freppledb.input.models.CalendarBucket
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class CalendarBucketAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.CalendarBucket.objects.all()
    # fields = ('id', 'calendar', 'startdate', 'enddate', 'value', 'priority', 'monday', 'tuesday', 'wednesday',
    #           'thursday', 'friday', 'saturday', 'sunday', 'starttime', 'endtime', 'source', 'lastmodified')

    serializer_class = CalendarBucketSerializer
    filter_class = CalendarBucketFilter
    ordering_fields = ('id')


class CalendarBucketdetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.CalendarBucket.objects.all()
    serializer_class = CalendarBucketSerializer


# CMARK begin LOCATION API-------------------------------------------------------
# CMARK 定义过滤
# class LocationFilter(filters.FilterSet):
#     # created_at 查询 创建在一段时间内
#     # [url例子] /api/input/location/?created_at_gte=2018-1-1&created_at_lte=2019-10-1
#     created_at_gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
#     created_at_lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
#
#     class Meta:
#         model = freppledb.input.models.Location
#         # owner__nr 定义为外键查询
#         # [url例子] /api/input/location/?owner__nr=l001
#         fields = (
#            'id', 'nr', 'name', 'area', 'owner', 'owner__nr', 'description', 'category', 'subcategory',
#            'available', 'source', 'created_at', 'updated_at')
# /api/input/location/?nr__contains=nr1&created_at__gte=2018-1-1&area=china
class LocationFilter(filters.FilterSet):
    # 时间使用这个方式,不然会发生类型错误
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.Location
        fields = {
            'id': ['exact', 'in'],
            'nr': ['exact', 'in', 'contains'],
            'name': ['exact', 'in', 'contains'],
            'area': ['exact', 'in', 'contains'],
            'owner__nr': ['exact'],
            'available': ['exact'],
            'category': ['exact', 'contains'],
            'subcategory': ['exact', 'contains'],
        }
        filter_fields = (
            'id', 'nr', 'name', 'area', 'owner__nr', 'category', 'subcategory', 'available', 'created_at', 'updated_at')


# 定义外键对象的显示
#  "owner": {
#                "id": 6,
#                "nr": "2-code",
#                "name": "2-name"
#            }
class LocationOwnerSerializer(ModelSerializer):
    class Meta:
        model = freppledb.input.models.Location
        fields = ('id', 'nr', 'name')
        # CMARK 写入参数, 用来更新外键, 如果没有这个配置, 那么产生不可写错误
        extra_kwargs = {
            'id': {
                'read_only': False,
                'required': False,
                'allow_null': True
            },
            'nr': {
                'read_only': False,
                'required': False,
                'allow_null': True
            },
            'name': {'allow_null': True}
        }


class LocationSerializer(BulkSerializerMixin, ModelSerializer):
    # 这个方法不好, 不适用left join, 是查询出来结果再遍历查询
    # owner_nr = serializers.CharField(source='owner.nr')
    owner = LocationOwnerSerializer(many=False, allow_null=True)
    # id readonly=False 不可以缺少
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.Location
        fields = ('id', 'nr', 'name', 'area', 'owner', 'description', 'category', 'subcategory',
                  'available', 'source', 'created_at', 'updated_at')
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


# CMARK LIST API
class LocationAPI(frePPleListCreateAPIView):
    # 基础查询
    queryset = freppledb.input.models.Location.objects.all()
    # 序列化类-定义字段相关内容
    serializer_class = LocationSerializer
    # 过滤类-查询相关内容
    filter_class = LocationFilter
    # 排序
    ordering_fields = ('id')
    # 自定义分页, 默认每页100
    # [url例子]/api/input/location/?page=2&pagesize=10


# CMARK 根据主键操作
class LocationdetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.Location.objects.all()
    serializer_class = LocationSerializer


# CMARK 根据自然键查询/删除
# TODO　多个自然键不支持
class LocationdetailNkAPI(frePPleRetrieveUpdateDestroyAPIView):
    # natural key 自然键
    lookup_field = 'nr'
    queryset = freppledb.input.models.Location.objects.all()
    serializer_class = LocationSerializer


# CMARK end LOCATION API-------------------------------------------------------

class CustomerFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.Customer
        fields = {
            'id': ['exact', 'in'],
            'nr': ['exact', 'in', 'contains'],
            'name': ['exact', 'in', 'contains'],
            'area': ['exact', 'in', 'contains'],
            'owner__nr': ['exact'],
            'available': ['exact'],
            'description': ['exact', 'contains'],
            'category': ['exact', 'contains'],
            'subcategory': ['exact', 'contains'],
            'source': ['exact', 'in'],
        }
        filter_fields = (
            'id', 'nr', 'name', 'area', 'owner__nr', 'available', 'description', 'category', 'subcategory', 'source',
            'created_at', 'updated_at')


class CustomerOwnerSerializer(ModelSerializer):
    class Meta:
        model = freppledb.input.models.Customer
        fields = ('id', 'nr', 'name')
        # CMARK 写入参数, 用来更新外键, 如果没有这个配置, 那么产生不可写错误
        extra_kwargs = {
            'id': {
                'read_only': False,
                'required': False,
                'allow_null': True
            },
            'nr': {
                'read_only': False,
                'required': False,
                'allow_null': True
            },
            'name': {'allow_null': True}
        }


class CustomerSerializer(BulkSerializerMixin, ModelSerializer):
    owner = CustomerOwnerSerializer(many=False, required=False, allow_null=True)
    # id readonly=False 不可以缺少
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.Customer
        # fields = ('name', 'owner', 'description', 'category', 'subcategory', 'source', 'lastmodified')
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class CustomerAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_class = CustomerFilter
    ordering_fields = ('id')


class CustomerdetailNkAPI(frePPleRetrieveUpdateDestroyAPIView):
    # natural key 自然键
    lookup_field = 'nr'
    queryset = freppledb.input.models.Customer.objects.all()
    serializer_class = CustomerSerializer


class CustomerdetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.Customer.objects.all()
    serializer_class = CustomerSerializer


class ItemFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.Item
        fields = {
            'id': ['exact', 'in'],
            'nr': ['exact', 'in', 'contains'],
            'name': ['exact', 'in', 'contains'],
            'owner__nr': ['exact'],
            'project_nr': ['exact'],
            'description': ['exact', 'contains'],
            'category': ['exact', 'contains'],
            'subcategory': ['exact', 'contains'],
            'cost': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'source': ['exact', 'in'],
        }
        filter_fields = (
            'id', 'nr', 'name', 'cost', 'owner__nr', 'source',
            'project_nr', 'description', 'category', 'subcategory', 'created_at', 'updated_at')


class ItemOwnerSerializer(ModelSerializer):
    class Meta:
        model = freppledb.input.models.Item
        fields = ('id', 'nr', 'name')
        # CMARK 写入参数, 用来更新外键, 如果没有这个配置, 那么产生不可写错误
        extra_kwargs = {
            'id': {
                'read_only': False,
                'required': False,
                'allow_null': True
            },
            'nr': {
                'read_only': False,
                'required': False,
                'allow_null': True
            },
            'name': {'allow_null': True}
        }


class ItemSerializer(BulkSerializerMixin, ModelSerializer):
    owner = ItemOwnerSerializer(many=False, allow_null=True)
    # id readonly=False 不可以缺少
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.Item
        # fields来明确字段，__all__表名包含所有字段
        fields = '__all__'
        # fields = ('name', 'owner', 'description', 'category', 'subcategory', 'cost', 'source', 'lastmodified')
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class ItemAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.Item.objects.all()
    serializer_class = ItemSerializer
    filter_class = ItemFilter
    # 排序
    ordering_fields = ('id')
    pagination_class = CustomerNumberPagination


class ItemdetailNkAPI(frePPleRetrieveUpdateDestroyAPIView):
    # natural key 自然键
    lookup_field = 'nr'
    queryset = freppledb.input.models.Item.objects.all()
    serializer_class = ItemSerializer


class ItemdetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.Item.objects.all()
    serializer_class = ItemSerializer


# CMARK begin itemlocation API---------------------------------------

class ItemLocationFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.ItemLocation
        fields = {
            'id': ['exact', 'in'],
            'item__nr': ['exact'],
            'location__nr': ['exact'],
            'project_nr': ['exact'],
            'description': ['exact', 'contains'],
            'category': ['exact', 'contains'],
            'subcategory': ['exact', 'contains'],
            'cost': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'source': ['exact', 'in'],
        }
        filter_fields = (
            'id', 'item__nr', 'location__nr', 'project_nr', 'description', 'category', 'subcategory', 'cost', 'source',
            'created_at', 'updated_at')


class ItemLocationSerializer(BulkSerializerMixin, ModelSerializer):
    item = ItemOwnerSerializer(many=False, allow_null=True)
    location = LocationOwnerSerializer(many=False, allow_null=True)
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.ItemLocation
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class ItemLocationAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.ItemLocation.objects.all()
    serializer_class = ItemLocationSerializer
    filter_class = ItemLocationFilter
    # 排序
    ordering_fields = ('id',)
    pagination_class = CustomerNumberPagination


# class ItemLocationdetailNkAPI(frePPleRetrieveUpdateDestroyAPIView):
#     # natural key 自然键
#     lookup_field = 'nr'
#     queryset = freppledb.input.models.ItemLocation.objects.all()
#     serializer_class = ItemLocationSerializer


class ItemLocationDetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.ItemLocation.objects.all()
    serializer_class = ItemLocationSerializer


# CMARK end itemlocation API-----------------------------------------


# CMARK begin itemclient API-----------------------------------------
class ItemCustomerFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name=("created_at", "update_at"), lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name=("created_at", "update_at"), lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.ItemCustomer
        fields = {
            'id': ['exact', 'in'],
            'sale_item__nr': ['exact'],
            'product_item__nr': ['exact'],
            'customer__nr': ['exact'],
            'location__nr': ['exact'],
            'customer_item_nr': ['exact', 'in'],
            'status': ['exact', 'in']
        }
        filter_fields = (
            'id', 'sale_item__nr', 'product_item__nr', 'customer__nr', 'location__nr', 'customer_item_nr', 'status',
            'created_at', 'updated_at')


class ItemCustomerSerializer(BulkSerializerMixin, ModelSerializer):
    # 这个方法不好, 不适用left join, 是查询出来结果再遍历查询
    # owner_nr = serializers.CharField(source='owner.nr')
    item = ItemOwnerSerializer(many=False, allow_null=True)
    product_item = ItemOwnerSerializer(many=False, allow_null=True)
    client = CustomerOwnerSerializer(many=False, allow_null=True)
    location = LocationOwnerSerializer(many=False, allow_null=True)
    # id readonly=False 不可以缺少
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.ItemCustomer
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class ItemCustomerAPI(frePPleListCreateAPIView):
    # 基础查询
    queryset = freppledb.input.models.ItemCustomer.objects.all()
    # 序列化类-定义字段相关内容
    serializer_class = ItemCustomerSerializer
    # 过滤类-查询相关内容
    filter_class = ItemCustomerFilter
    # 排序
    ordering_fields = ('id',)


class ItemCustomerdetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.ItemCustomer.objects.all()
    serializer_class = ItemCustomerSerializer


# CMARK begin ItemSuccessor API-----------------------------------------
class ItemSuccessorFilter(filters.FilterSet):
    # 时间使用这个方式,不然会发生类型错误
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.ItemSuccessor
        fields = {
            'id': ['exact', 'in'],
            'item__nr': ['exact'],
            'item_successor__nr': ['exact'],
            'priority': ['exact', 'in'],
            'ratio': ['exact', 'in'],

        }
        filter_fields = (
            'id', 'item__nr', 'item_successor__nr', 'priority', 'ratio', 'created_at', 'updated_at')


class ItemSuccessorSerializer(BulkSerializerMixin, ModelSerializer):
    # 这个方法不好, 不适用left join, 是查询出来结果再遍历查询
    # owner_nr = serializers.CharField(source='owner.nr')
    item = ItemOwnerSerializer(many=False, allow_null=True)
    item_successor = ItemOwnerSerializer(many=False, allow_null=True)
    # id readonly=False 不可以缺少
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.ItemSuccessor
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class ItemSuccessorAPI(frePPleListCreateAPIView):
    # 基础查询
    queryset = freppledb.input.models.ItemSuccessor.objects.all()
    # 序列化类-定义字段相关内容
    serializer_class = ItemSuccessorSerializer
    # 过滤类-查询相关内容
    filter_class = ItemSuccessorFilter
    # 排序
    ordering_fields = ('id')


class ItemSuccessordetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.ItemSuccessor.objects.all()
    serializer_class = ItemSuccessorSerializer


# CMARK begin supplier API-----------------------------------------
class SupplierFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.Supplier
        fields = {
            'id': ['exact', 'in'],
            'nr': ['exact', 'in', 'contains'],
            'name': ['exact', 'in', 'contains'],
            'area': ['exact', 'contains'],
            'address': ['exact', 'contains'],
            'ship_address': ['exact', 'contains'],
            'owner__nr': ['exact'],
            'available': ['exact'],
            'description': ['exact', 'contains'],
            'category': ['exact', 'contains'],
            'subcategory': ['exact', 'contains'],
            'source': ['exact', 'in'],
        }
        filter_fields = (
            'id', 'nr', 'name', 'area', 'address', 'ship_address', 'source', 'available', 'owner__nr',
            'category', 'subcategory', 'description', 'created_at', 'updated_at')


class SupplierOwnerSerializer(ModelSerializer):
    class Meta:
        model = freppledb.input.models.Supplier
        fields = ('id', 'nr', 'name')
        # CMARK 写入参数, 用来更新外键, 如果没有这个配置, 那么
        extra_kwargs = {
            'id': {
                'read_only': False,
                'required': False,
                'allow_null': True
            },
            'name': {
                'read_only': False,
                'required': False,
                'allow_null': True
            },
            'nr': {'allow_null': True}
        }


class SupplierSerializer(BulkSerializerMixin, ModelSerializer):
    owner = SupplierOwnerSerializer(many=False, allow_null=True)
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.Supplier
        # fields = ('name', 'owner', 'description', 'category', 'subcategory', 'source', 'lastmodified')
        # filter_fields = (
        #     'id', 'nr', 'name', 'area', 'address', 'ship_address', 'source', 'available', 'owner', 'category',
        #     'subcategory', 'description', 'created_at', 'updated_at', 'lastmodified')
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class SupplierAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.Supplier.objects.all()
    serializer_class = SupplierSerializer
    # filter_fields = (
    #     'id', 'nr', 'name', 'area', 'address', 'ship_address', 'source', 'available', 'owner', 'category',
    #     'subcategory', 'description', 'created_at', 'updated_at', 'lastmodified')
    filter_class = SupplierFilter
    ordering_fields = ('id')
    pagination_class = CustomerNumberPagination


class SupplierdetailNkAPI(frePPleRetrieveUpdateDestroyAPIView):
    # natural key 自然键
    lookup_field = 'nr'
    queryset = freppledb.input.models.Supplier.objects.all()
    serializer_class = SupplierSerializer


class SupplierdetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.Supplier.objects.all()
    serializer_class = SupplierSerializer


# CMARK end Supplier API-------------------------------------------------------

class ItemSupplierFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    # /api/input/location/?nr__contains=nr1&created_at__gte=2018-1-1&area=china
    class Meta:
        model = freppledb.input.models.ItemSupplier
        fields = {'id': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'item__nr': ['exact', 'in', ],
                  'supplier__nr': ['exact', 'in'],
                  'status': ['exact', 'in'],
                  'cost': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'monetary_unit': ['exact', 'in'],
                  'cost_unit': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'priority': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'moq': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'effective_start': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'effective_end': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'source': ['exact', 'in', ], }
        filter_fields = (
            'id', 'item__nr', 'supplier__nr', 'status', 'cost', 'monetary_unit', 'cost_unit', 'priority', 'moq',
            'effective_start', 'effective_end', 'source', 'created_at', 'updated_at')


class ItemSupplierSerializer(BulkSerializerMixin, ModelSerializer):
    item = ItemOwnerSerializer(many=False, allow_null=True)
    supplier = SupplierOwnerSerializer(many=False, allow_null=True)
    # id readonly=False 不可以缺少
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.ItemSupplier
        # fields = ('id', 'item', 'location', 'supplier', 'leadtime', 'sizeminimum', 'sizemultiple',
        #           'cost', 'priority', 'effective_start', 'effective_end', 'source', 'lastmodified')
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class ItemSupplierAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.ItemSupplier.objects.all()
    serializer_class = ItemSupplierSerializer
    filter_class = ItemSupplierFilter
    ordering_fields = ('id')


class ItemSupplierdetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.ItemSupplier.objects.all()
    serializer_class = ItemSupplierSerializer


class ItemSupplierNkAPI(frePPleRetrieveUpdateDestroyAPIView):
    # natural key 自然键
    lookup_field = 'nr'
    queryset = freppledb.input.models.Location.objects.all()
    serializer_class = LocationSerializer


# CMARK end ItemSupplier API-------------------------------------------------------


# /api/input/location/?nr__contains=nr1&created_at__gte=2018-1-1&area=china
class ItemDistributionFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.ItemDistribution
        fields = {
            'id': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'item__name': ['exact', ],
            'origin__name': ['exact', ],
            'destination__name': ['exact'],
            'priority': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
        }
        filter_fields = (
            'id', 'item__name', 'origin__name', 'destination__name', 'priority', 'created_at', 'updated_at')


class ItemDistributionSerializer(BulkSerializerMixin, ModelSerializer):
    item = ItemOwnerSerializer(many=False, allow_null=True)
    id = serializers.IntegerField(read_only=False)
    origin = LocationOwnerSerializer(many=False, allow_null=True)
    destination = LocationOwnerSerializer(many=False, allow_null=True)

    class Meta:
        model = freppledb.input.models.ItemDistribution
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class ItemDistributionAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.ItemDistribution.objects.all()
    serializer_class = ItemDistributionSerializer
    filter_class = ItemDistributionFilter
    ordering_fields = ('id')
    pagination_class = CustomerNumberPagination


class ItemDistributiondetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.ItemDistribution.objects.all()
    serializer_class = ItemDistributionSerializer


class OperationFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.Operation
        fields = {
            'id': ['exact', 'in'],
            'nr': ['exact', 'in', 'contains'],
            'name': ['exact', 'in', 'contains'],
            'location__nr': ['exact'],
            'available__name': ['exact'],
            'category': ['exact', 'contains'],
            'subcategory': ['exact', 'contains'],
            'min_num_per': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'max_num_per': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'multiple_per': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'cost_per': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'duration_per': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ], }

        filter_fields = ('id', 'nr',
                         'name', 'location__nr', 'available__name', 'category', 'subcategory',
                         'min_num_per', 'max_num_per', 'multiple_per', 'cost_per',
                         'duration_per', 'created_at', 'updated_at')


class OperationSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = freppledb.input.models.Operation
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class OperationAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.Operation.objects.all()
    serializer_class = OperationSerializer
    filter_class = OperationFilter


class OperationdetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.Operation.objects.all()
    serializer_class = OperationSerializer


class SubOperationFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.SubOperation
        fields = {
            'id': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'parent_operation__nr': ['exact', 'in', ],
            'priority': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'suboperation__nr': ['exact', 'in', ],
            'effective_start': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'effective_end': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
        }

        filter_fields = (
            'id', 'parent_operation__nr', 'suboperation__nr', 'priority', 'effective_start', 'effective_end',
            'created_at', 'updated_at')


class SubOperationSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = freppledb.input.models.SubOperation
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class SubOperationAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.SubOperation.objects.all()
    serializer_class = SubOperationSerializer
    filter_class = SubOperationFilter


class SubOperationdetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.SubOperation.objects.all()
    serializer_class = SubOperationSerializer


# CMARK start InventoryParameter API-------------------------------------------------------
class InventoryParameterFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.InventoryParameter
        fields = {
            'id': ['exact', 'in'],
            'item__nr': ['exact'],
            'location__nr': ['exact'],
            'rop_cover_period': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'rop': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'rop_by_system': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'safetystock_cover_period': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'safetysotck_min_qty': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'safetysotck_max_qty': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'safetystock_qty_by_system': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'service_level': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
        }
        filter_fields = (
            'id', 'item__nr', 'location__nr', 'rop_cover_period', 'rop', 'rop_by_system',
            'safetystock_cover_period', 'safetysotck_min_qty', 'safetysotck_max_qty', 'safetystock_qty_by_system',
            'service_level', 'created_at', 'updated_at')


class InventoryParameterSerializer(BulkSerializerMixin, ModelSerializer):
    item = ItemOwnerSerializer(many=False, allow_null=True)
    location = LocationOwnerSerializer(many=False, allow_null=True)
    # id readonly=False 不可以缺少
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.InventoryParameter
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class InventoryParameterAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.InventoryParameter.objects.all()
    serializer_class = InventoryParameterSerializer
    filter_class = InventoryParameterFilter
    ordering_fields = ('id',)
    pagination_class = CustomerNumberPagination


class InventoryParameterDetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.InventoryParameter.objects.all()
    serializer_class = InventoryParameterSerializer


# CMARK end InventoryParameter API-------------------------------------------------------

# CMARK start SalesOrder API-------------------------------------------------------
class SalesOrderFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.SalesOrder
        fields = {
            'id': ['exact', 'in'],
            'nr': ['exact'],
            'location__nr': ['exact'],
            'customer__nr': ['exact'],
            'status': ['exact'],
            'max_lateness': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'min_shipment': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
        }
        filter_fields = (
            'id', 'nr', 'location__nr', 'customer__nr', 'status', 'max_lateness'
                                                                  'min_shipment', 'created_at', 'updated_at')


class SalesOrderOwnerSerializer(ModelSerializer):
    location = LocationOwnerSerializer(many=False, allow_null=True)
    customer = CustomerOwnerSerializer(many=False, allow_null=True)

    class Meta:
        model = freppledb.input.models.SalesOrder
        fields = ('id', 'nr', 'location', 'customer')
        # CMARK 写入参数, 用来更新外键, 如果没有这个配置, 那么产生不可写错误
        extra_kwargs = {
            'id': {
                'read_only': False,
                'required': False,
                'allow_null': True
            },
            'nr': {
                'read_only': False,
                'required': False,
                'allow_null': True
            },
            'location': {'allow_null': True},
            'customer': {'allow_null': True},
        }


class SalesOrderSerializer(BulkSerializerMixin, ModelSerializer):
    customer = CustomerOwnerSerializer(many=False, allow_null=True)
    location = LocationOwnerSerializer(many=False, allow_null=True)
    # id readonly=False 不可以缺少
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.SalesOrder
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class SalesOrderAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    filter_class = SalesOrderFilter
    ordering_fields = ('id',)
    pagination_class = CustomerNumberPagination


class SalesOrderDetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer


# CMARK end SalesOrderItem API-------------------------------------------------------


# CMARK start SalesOrderItem API-------------------------------------------------------
class SalesOrderItemFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.SalesOrderItem
        fields = {
            'id': ['exact', 'in'],
            'sales_order__nr': ['exact'],
            'item__nr': ['exact'],
            'line_no': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'qty': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'schedule_qty': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'deliver_qty': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'due': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'priority': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'status': ['exact'],
            'max_lateness': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'min_shipment': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
        }
        filter_fields = (
            'id', 'item__nr', 'sales_order__nr', 'line_no', 'qty', 'schedule_qty',
            'deliver_qty', 'due', 'priority', 'status', 'max_lateness',
            'min_shipment', 'created_at', 'updated_at')


class SalesOrderItemSerializer(BulkSerializerMixin, ModelSerializer):
    item = ItemOwnerSerializer(many=False, allow_null=True)
    sales_order = SalesOrderOwnerSerializer(many=False, allow_null=True)
    # id readonly=False 不可以缺少
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.SalesOrderItem
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class SalesOrderItemAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.SalesOrderItem.objects.all()
    serializer_class = SalesOrderItemSerializer
    filter_class = SalesOrderItemFilter
    ordering_fields = ('id',)
    pagination_class = CustomerNumberPagination


class SalesOrderItemDetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.SalesOrderItem.objects.all()
    serializer_class = SalesOrderItemSerializer


# CMARK end SalesOrderItem API-------------------------------------------------------

# CMARK start DeliveryOrder API-------------------------------------------------------
# TODO 未完成，deliver,deliver_source
class DeliveryOrderFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.DeliveryOrder
        fields = {
            'id': ['exact', 'in'],
            'nr': ['exact'],
            'source_location__nr': ['exact'],
            'destination_location__nr': ['exact'],
            'deliver__nr': ['exact'],
            'deliver_source__id': ['exact'],
            'type': ['exact', 'in'],
            'status': ['exact', 'in'],
            'schedule_arrive_at': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'start_ship_at': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'actual_arrive_at': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'delay': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
        }
        filter_fields = (
            'id', 'nr', 'source_location__nr', 'destination_location__nr', 'deliver__nr', 'deliver_source__id', 'qty',
            'status', 'schedule_arrive_at', 'start_ship_at', 'actual_arrive_at', 'delay',
            'created_at', 'updated_at')


class DeliveryOrderOwnerSerializer(ModelSerializer):
    source_location = LocationOwnerSerializer(many=False, allow_null=True)
    destination_location = LocationOwnerSerializer(many=False, allow_null=True)

    class Meta:
        model = freppledb.input.models.DeliveryOrder
        fields = ('id', 'nr', 'source_location', 'destination_location')
        # CMARK 写入参数, 用来更新外键, 如果没有这个配置, 那么产生不可写错误
        extra_kwargs = {
            'id': {
                'read_only': False,
                'required': False,
                'allow_null': True
            },
            'nr': {
                'read_only': False,
                'required': False,
                'allow_null': True
            },
            'source_location': {'allow_null': True},
            'destination_location': {'allow_null': True}
        }


class DeliveryOrderSerializer(BulkSerializerMixin, ModelSerializer):
    source_location = LocationOwnerSerializer(many=False, allow_null=True)
    destination_location = LocationOwnerSerializer(many=False, allow_null=True)
    # id readonly=False 不可以缺少
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.DeliveryOrder
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class DeliveryOrderAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.DeliveryOrder.objects.all()
    serializer_class = DeliveryOrderSerializer
    filter_class = DeliveryOrderFilter
    ordering_fields = ('id',)
    pagination_class = CustomerNumberPagination


class DeliveryOrderDetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.DeliveryOrder.objects.all()
    serializer_class = DeliveryOrderSerializer


# CMARK end DeliveryOrder API-------------------------------------------------------

# CMARK start DeliveryOrderItem API-------------------------------------------------------
# TODO 未完成，deliver,deliver_source
class DeliveryOrderItemFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.DeliveryOrderItem
        fields = {
            'id': ['exact', 'in'],
            'line_no': ['exact', 'in'],
            'item__nr': ['exact'],
            'delivery_order__nr': ['exact'],
            'deliver_source__id': ['exact'],
            'deliver_qty': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'status': ['exact', 'in'],
            'start_ship_at': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'actual_arrive_at': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'delay': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
        }
        filter_fields = (
            'id', 'line_no', 'item__nr', 'delivery_order__nr', 'deliver_source__id', 'deliver_qty',
            'status', 'start_ship_at', 'actual_arrive_at', 'delay',
            'created_at', 'updated_at')


class DeliveryOrderItemSerializer(BulkSerializerMixin, ModelSerializer):
    item = ItemOwnerSerializer(many=False, allow_null=True)
    delivery_order = DeliveryOrderOwnerSerializer(many=False, allow_null=True)
    # id readonly=False 不可以缺少
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.DeliveryOrderItem
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class DeliveryOrderItemAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.DeliveryOrder.objects.all()
    serializer_class = DeliveryOrderItemSerializer
    filter_class = DeliveryOrderItemFilter
    ordering_fields = ('id',)
    pagination_class = CustomerNumberPagination


class DeliveryOrderItemDetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.DeliveryOrderItem.objects.all()
    serializer_class = DeliveryOrderItemSerializer


# CMARK end SalesOrderItem API-------------------------------------------------------

# CMARK start PurchaseOrder API-------------------------------------------------------

class PurchaseOrderFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.PurchaseOrder
        fields = {
            'id': ['exact', 'in'],
            'nr': ['exact'],
            'location__nr': ['exact'],
            'supplier__nr': ['exact'],
            'status': ['exact', 'in'],
            'delay': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
        }
        filter_fields = (
            'id', 'nr', 'location__nr', 'supplier__nr', 'status',
            'delay','created_at', 'updated_at')


class PurchaseOrderOwnerSerializer(ModelSerializer):
    location = LocationOwnerSerializer(many=False, allow_null=True)
    supplier = SupplierOwnerSerializer(many=False, allow_null=True)

    class Meta:
        model = freppledb.input.models.PurchaseOrder
        fields = ('id', 'nr', 'location', 'supplier')
        # CMARK 写入参数, 用来更新外键, 如果没有这个配置, 那么产生不可写错误
        extra_kwargs = {
            'id': {
                'read_only': False,
                'required': False,
                'allow_null': True
            },
            'nr': {
                'read_only': False,
                'required': False,
                'allow_null': True
            },
            'location': {'allow_null': True},
            'supplier': {'allow_null': True}
        }


class PurchaseOrderSerializer(BulkSerializerMixin, ModelSerializer):
    location = LocationOwnerSerializer(many=False, allow_null=True)
    supplier = SupplierOwnerSerializer(many=False, allow_null=True)
    # id readonly=False 不可以缺少
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.PurchaseOrder
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class PurchaseOrderAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    filter_class = PurchaseOrderFilter
    ordering_fields = ('id',)
    pagination_class = CustomerNumberPagination


class PurchaseOrderDetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer


# CMARK end PurchaseOrder API-------------------------------------------------------

# CMARK start PurchaseOrderItem API-------------------------------------------------------

class PurchaseOrderItemFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.PurchaseOrderItem
        fields = {
            'id': ['exact', 'in'],
            'line_no': ['exact'],
            'item__nr': ['exact'],
            'purchase_order__nr': ['exact'],
            'status': ['exact', 'in'],
            'delay': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'qty': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
        }
        filter_fields = (
            'id', 'line_no', 'item__nr', 'purchase_order__nr', 'status',
            'delay','qty','created_at', 'updated_at')


class PurchaseOrderItemSerializer(BulkSerializerMixin, ModelSerializer):
    item = ItemOwnerSerializer(many=False, allow_null=True)
    purchase_order = PurchaseOrderOwnerSerializer(many=False, allow_null=True)
    # id readonly=False 不可以缺少
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.PurchaseOrderItem
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class PurchaseOrderItemAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderItemSerializer
    filter_class = PurchaseOrderItemFilter
    ordering_fields = ('id',)
    pagination_class = CustomerNumberPagination


class PurchaseOrderItemDetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderItemSerializer


# CMARK end PurchaseOrderItem API-------------------------------------------------------

# CMARK start WorkOrder API-------------------------------------------------------

class WorkOrderFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.WorkOrder
        fields = {
            'id': ['exact', 'in'],
            'nr': ['exact'],
            'location__nr': ['exact'],
            'status': ['exact', 'in'],
            'delay': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
        }
        filter_fields = (
            'id', 'nr', 'location__nr', 'status', 'delay', 'created_at', 'updated_at')


class WorkOrderOwnerSerializer(ModelSerializer):
    location = LocationOwnerSerializer(many=False, allow_null=True)

    class Meta:
        model = freppledb.input.models.WorkOrder
        fields = ('id', 'nr', 'location')
        extra_kwargs = {
            'id': {
                'read_only': False,
                'required': False,
                'allow_null': True
            },
            'nr': {
                'read_only': False,
                'required': False,
                'allow_null': True
            },
            'location': {'allow_null': True},
        }


class WorkOrderSerializer(BulkSerializerMixin, ModelSerializer):
    location = LocationOwnerSerializer(many=False, allow_null=True)
    # id readonly=False 不可以缺少
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.WorkOrder
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class WorkOrderAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer
    filter_class = WorkOrderFilter
    ordering_fields = ('id',)
    pagination_class = CustomerNumberPagination


class WorkOrderDetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer


# CMARK end WorkOrder API-------------------------------------------------------

# CMARK start WorkOrderItem API-------------------------------------------------------

class WorkOrderItemFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.WorkOrderItem
        fields = {
            'id': ['exact', 'in'],
            'item__nr': ['exact'],
            'workorder__nr': ['exact'],
            'status': ['exact', 'in'],
            'delay': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'qty': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'finished_qty': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
        }
        filter_fields = (
            'id', 'item__nr', 'workorder__nr','status', 'delay','qty','finished_qty', 'created_at', 'updated_at')


class WorkOrderItemSerializer(BulkSerializerMixin, ModelSerializer):
    workorder = WorkOrderOwnerSerializer(many=False, allow_null=True)
    item = ItemOwnerSerializer(many=False, allow_null=True)
    # id readonly=False 不可以缺少
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = freppledb.input.models.WorkOrderItem
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class WorkOrderItemAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.WorkOrderItem.objects.all()
    serializer_class = WorkOrderItemSerializer
    filter_class = WorkOrderItemFilter
    ordering_fields = ('id',)
    pagination_class = CustomerNumberPagination


class WorkOrderItemDetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.WorkOrderItem.objects.all()
    serializer_class = WorkOrderItemSerializer


# CMARK end WorkOrderItem API-------------------------------------------------------


class BufferFilter(filters.FilterSet):
    class Meta:
        model = freppledb.input.models.Buffer
        fields = {'name': ['exact', 'in', 'contains', ], 'description': ['exact', 'contains', ],
                  'category': ['exact', 'contains', ], 'subcategory': ['exact', 'contains', ],
                  'type': ['exact', 'in', ], 'location': ['exact', 'in', ], 'item': ['exact', 'in', ],
                  'onhand': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'minimum': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'minimum_calendar': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'min_interval': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'source': ['exact', 'in', ], 'lastmodified': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ], }

        filter_fields = (
            'name', 'description', 'category', 'subcategory', 'type', 'location',
            'item', 'onhand', 'minimum', 'minimum_calendar', 'min_interval',
            'source', 'lastmodified'
        )


class BufferSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = freppledb.input.models.Buffer
        fields = (
            'name', 'description', 'category', 'subcategory', 'type', 'location',
            'item', 'onhand', 'minimum', 'minimum_calendar', 'min_interval',
            'source', 'lastmodified'
        )
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'name'
        partial = True


class BufferAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.Buffer.objects.all()
    serializer_class = BufferSerializer
    filter_fields = (
        'name', 'description', 'category', 'subcategory', 'type', 'location',
        'item', 'onhand', 'minimum', 'minimum_calendar', 'min_interval',
        'source', 'lastmodified'
    )
    filter_class = BufferFilter


class BufferdetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.Buffer.objects.all()
    serializer_class = BufferSerializer


class SetupMatrixFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.SetupMatrix
        fields = {
            'id': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'name': ['exact', 'in', 'contains', ],
            'source': ['exact', 'in', ]}

        filter_fields = (
            'id', 'name', 'source', 'created_at', 'updated_at'
        )


class SetupMatrixSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = freppledb.input.models.SetupMatrix
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class SetupMatrixAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.SetupMatrix.objects.all()
    serializer_class = SetupMatrixSerializer
    filter_class = SetupMatrixFilter


class SetupMatrixdetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.SetupMatrix.objects.all()
    serializer_class = SetupMatrixSerializer


class SetupRuleFilter(filters.FilterSet):
    class Meta:
        model = freppledb.input.models.SetupRule
        fields = {
            'id': ['exact', 'in', 'contains', ],
            'setupmatrix': ['exact', 'in', ],
            'fromsetup': ['exact', 'in', ],
            'tosetup': ['exact', 'in', ],
            'priority': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'duration': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'cost': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
        }

        filter_fields = ('id', 'setupmatrix', 'fromsetup', 'tosetup', 'priority', 'duration', 'cost')


class SetupRuleSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = freppledb.input.models.SetupRule
        fields = ('id', 'setupmatrix', 'fromsetup', 'tosetup', 'priority', 'duration', 'cost')
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'setupmatrix'
        partial = True


class SetupRuleAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.SetupRule.objects.all()
    serializer_class = SetupRuleSerializer
    filter_class = SetupRuleFilter


class SetupRuledetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.SetupRule.objects.all()
    serializer_class = SetupRuleSerializer


class ResourceFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.Resource
        fields = {
            'id': ['exact', 'in'],
            'nr': ['exact', 'in', 'contains'],
            'name': ['exact', 'in', 'contains', ],
            'owner__nr': ['exact'],
            'maximum_calendar__name': ['exact'],
            'available__name': ['exact'],
            'location__nr': ['exact'],
            'efficiency_calendar__name': ['exact'],
            'setupmatrix__nr': ['exact'],

            'description': ['exact', 'contains', ],
            'category': ['exact', 'contains', ],
            'subcategory': ['exact', 'contains', ],
            'type': ['exact', 'in', ],
            'maximum': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'cost': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
        }

        filter_fields = ('id', 'nr', 'name', 'owner__nr', 'maximum_calendar__name', 'available__name', 'location__nr',
                         'efficiency_calendar__name', 'setupmatrix__nr', 'description', 'category', 'subcategory',
                         'type', 'maximum', 'cost', 'created_at', 'updated_at')


class ResourceSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = freppledb.input.models.Resource
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True  # 允许部分字段更新


class ResourceAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.Resource.objects.all()
    serializer_class = ResourceSerializer
    filter_class = ResourceFilter


class ResourcedetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.Resource.objects.all()
    serializer_class = ResourceSerializer


class SkillFilter(filters.FilterSet):
    class Meta:
        model = freppledb.input.models.Skill
        fields = {
            'id': ['exact', 'in'],
            'nr': ['exact', 'in', 'contains'],
            'name': ['exact', 'in', 'contains', ]}
        filter_fields = ('id', 'nr', 'name')


class SkillSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = freppledb.input.models.Skill
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class SkillAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.Skill.objects.all()
    serializer_class = SkillSerializer
    filter_class = SkillFilter


class SkilldetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.Skill.objects.all()
    serializer_class = SkillSerializer


class SkilldetailNkAPI(frePPleRetrieveUpdateDestroyAPIView):
    lookup_field = 'nr'
    queryset = freppledb.input.models.Skill.objects.all()
    serializer_class = SkillSerializer


class ResourceSkillFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.ResourceSkill
        fields = {
            'id': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'resource__nr': ['exact', 'in', ],
            'skill__nr': ['exact', 'in', ],
            'effective_start': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'effective_end': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'priority': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
        }

        filter_fields = (
            'id', 'resource__nr', 'skill__nr', 'effective_start', 'effective_end', 'priority', 'created_at',
            'updated_at')


class ResourceSkillSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = freppledb.input.models.ResourceSkill
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class ResourceSkillAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.ResourceSkill.objects.all()
    serializer_class = ResourceSkillSerializer
    filter_class = ResourceSkillFilter


class ResourceSkilldetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.ResourceSkill.objects.all()
    serializer_class = ResourceSkillSerializer


class OperationMaterialFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.OperationMaterial
        fields = {
            'id': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'quantity': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'quantity_fixed': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'materialbatch_per': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'operation__nr': ['exact', 'in', ],
            'item__nr': ['exact', 'in', ],
            'type': ['exact', 'in', ],
            'effective_start': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'effective_end': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'priority': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
        }

        filter_fields = (
            'id', 'operation__nr', 'item__nr', 'quantity', 'quantity_fixed', 'materialbatch_per', 'type',
            'effective_start', 'effective_end', 'priority', 'search', 'created_at', 'updated_at')


class OperationMaterialSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = freppledb.input.models.OperationMaterial
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class OperationMaterialAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.OperationMaterial.objects.all()
    serializer_class = OperationMaterialSerializer
    filter_class = OperationMaterialFilter


class OperationMaterialdetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.OperationMaterial.objects.all()
    serializer_class = OperationMaterialSerializer


class OperationResourceFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.OperationResource
        fields = {
            'id': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'operation__nr': ['exact', 'in', ],
            'resource__nr': ['exact', 'in', ], 'skill__nr': ['exact', 'in', ],
            'quantity': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'effective_start': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'effective_end': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'priority': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
            'setup': ['exact', 'in', 'contains', ],
            # 'search': ['exact', 'contains', ],
            # 'source': ['exact', 'in', ],
        }

        filter_fields = (
            'id', 'operation__nr', 'resource__nr', 'skill__nr', 'quantity', 'effective_start', 'effective_end',
            'priority', 'setup', 'created_at', 'updated_at')


class OperationResourceSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = freppledb.input.models.OperationResource
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class OperationResourceAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.OperationResource.objects.all()
    serializer_class = OperationResourceSerializer
    filter_class = OperationResourceFilter


class OperationResourcedetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.OperationResource.objects.all()
    serializer_class = OperationResourceSerializer


class ManufacturingOrderFilter(filters.FilterSet):
    class Meta:
        model = freppledb.input.models.ManufacturingOrder
        fields = {'id': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ], 'status': ['exact', 'in', ],
                  'reference': ['exact', 'in', 'contains', ], 'operation': ['exact', 'in', ],
                  'quantity': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'startdate': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'enddate': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'criticality': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'delay': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'plan': ['exact', 'in', 'contains', ], 'owner': ['exact', 'in'],
                  'source': ['exact', 'in', ], 'lastmodified': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ], }

        filter_fields = ('id', 'status', 'reference', 'operation', 'quantity', 'startdate', 'enddate',
                         'criticality', 'delay', 'plan', 'owner', 'source', 'lastmodified')


class ManufacturingOrderSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = freppledb.input.models.ManufacturingOrder
        fields = ('id', 'status', 'reference', 'operation', 'quantity', 'startdate', 'enddate',
                  'criticality', 'delay', 'plan', 'owner', 'source', 'lastmodified')
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class ManufacturingOrderAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.ManufacturingOrder.objects.all()
    serializer_class = ManufacturingOrderSerializer
    filter_class = ManufacturingOrderFilter


class ManufacturingOrderdetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.ManufacturingOrder.objects.all()
    serializer_class = ManufacturingOrderSerializer


class DistributionOrderFilter(filters.FilterSet):
    class Meta:
        model = freppledb.input.models.DistributionOrder
        fields = {'id': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ], 'status': ['exact', 'in', ],
                  'reference': ['exact', 'in', 'contains', ], 'item': ['exact', 'in', ],
                  'origin': ['exact', 'in', ], 'destination': ['exact', 'in', ],
                  'quantity': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'startdate': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'enddate': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'criticality': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'delay': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'plan': ['exact', 'in', 'contains', ],
                  'source': ['exact', 'in', ], 'lastmodified': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ], }

        filter_fields = ('id', 'status', 'reference', 'item', 'origin', 'destination', 'quantity',
                         'startdate', 'enddate', 'criticality', 'delay', 'plan', 'source', 'lastmodified')


class DistributionOrderSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = freppledb.input.models.DistributionOrder
        fields = ('id', 'reference', 'status', 'item', 'origin', 'destination', 'quantity',
                  'startdate', 'enddate', 'criticality', 'delay', 'plan', 'source', 'lastmodified')
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class DistributionOrderAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.DistributionOrder.objects.all()
    serializer_class = DistributionOrderSerializer
    filter_class = DistributionOrderFilter


class DistributionOrderdetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.DistributionOrder.objects.all()
    serializer_class = DistributionOrderSerializer

# CMARK begin ForecastYear API-------------------------------------------------------
class ForecastYearFilter(filters.FilterSet):
    class Meta:
        model = freppledb.input.models.ForecastYear
        fields = {
            'id': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'item__nr': ['exact'],
            'location__nr': ['exact'],
            'customer__nr': ['exact'],
            'year': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'date_number': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'ratio': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
        }
        filter_fields = (
            'id', 'item__nr', 'location__nr', 'customer__nr', 'year', 'date_number', 'ratio')


class ForecastYearSerializer(BulkSerializerMixin, ModelSerializer):
    item = ItemOwnerSerializer(many=False, allow_null=True)
    location = LocationOwnerSerializer(many=False, allow_null=True)
    customer = CustomerOwnerSerializer(many=False, allow_null=True)

    class Meta:
        model = freppledb.input.models.ForecastYear
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class ForecastYearAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.ForecastYear.objects.all()
    serializer_class = ForecastYearSerializer
    filter_class = ForecastYearFilter


class ForecastYeardetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.ForecastYear.objects.all()
    serializer_class = ForecastYearSerializer


# CMARK end ForecastYear API-------------------------------------------------------

# CMARK begin ForecastVersion API-------------------------------------------------------
class ForecastVersionFilter(filters.FilterSet):
    class Meta:
        model = freppledb.input.models.ForecastVersion
        fields = {
            'nr': ['exact', 'in'],
            'create_user__username': ['exact', 'in'],
            'status': ['exact', 'in'],
        }
        filter_fields = (
            'nr', 'create_user__username', 'status')


class ForecastVersionSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = freppledb.input.models.ForecastVersion
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        # update_lookup_field = 'id'
        partial = True


class ForecastVersionAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.ForecastVersion.objects.all()
    serializer_class = ForecastVersionSerializer
    filter_class = ForecastVersionFilter
    # ordering_fields = ('-id')


class ForecastVersiondetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.ForecastVersion.objects.all()
    serializer_class = ForecastVersionSerializer


# CMARK end ForecastVersion API--------------------------------------------------
# CMARK begin Forecast API-------------------------------------------------------
class ForecastFilter(filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')
    updated_at__gte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='gte')
    updated_at__lte = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr='lte')

    class Meta:
        model = freppledb.input.models.Forecast
        fields = {
            'id': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'item__nr': ['exact'],
            'location__nr': ['exact'],
            'customer__nr': ['exact'],
            'year': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'date_number': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'ratio': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
            'version': ['exact', 'in', 'gt', 'gte', 'lt', 'lte'],
        }
        filter_fields = (
            'id', 'item__nr', 'location__nr', 'customer__nr', 'year', 'date_number', 'ratio', 'version', 'create_at',
            'updated_at')


class ForecastSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = freppledb.input.models.Forecast
        fields = '__all__'
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'id'
        partial = True


class ForecastAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.Forecast.objects.all()
    serializer_class = ForecastSerializer
    filter_class = ForecastFilter
    ordering_fields = ('-id')


class ForecastdetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.Forecast.objects.all()
    serializer_class = ForecastSerializer


class ForecastdetailVersionAPI(frePPleRetrieveUpdateDestroyAPIView):
    lookup_field = 'version'
    queryset = freppledb.input.models.Forecast.objects.all()
    serializer_class = ForecastSerializer


# CMARK end ForecastVersion API-------------------------------------------------------




class DemandFilter(filters.FilterSet):
    class Meta:
        model = freppledb.input.models.Demand
        fields = {'name': ['exact', 'in', 'contains', ], 'description': ['exact', 'in', 'contains', ],
                  'category': ['exact', 'in', 'contains', ], 'subcategory': ['exact', 'in', 'contains', ],
                  'item': ['exact', 'in', ], 'customer': ['exact', 'in', ], 'location': ['exact', 'in', ],
                  'due': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ], 'status': ['exact', 'in', ],
                  'operation': ['exact', 'in', ], 'quantity': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'priority': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'delay': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'plannedquantity': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'deliverydate': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'plan': ['exact', 'in', 'contains', ], 'minshipment': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ],
                  'maxlateness': ['exact', 'in', 'gt', 'gte', 'lt', 'lte', ], }

        filter_fields = ('name', 'description', 'category', 'subcategory', 'item', 'customer', 'location', 'due',
                         'status', 'operation', 'quantity', 'priority', 'delay', 'plannedquantity', 'deliverydate',
                         'plan', 'minshipment', 'maxlateness')


class DemandSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = freppledb.input.models.Demand
        fields = ('name', 'description', 'category', 'subcategory', 'item', 'customer', 'location', 'due',
                  'status', 'operation', 'quantity', 'priority', 'delay', 'plannedquantity', 'deliverydate', 'plan',
                  'minshipment', 'maxlateness')
        list_serializer_class = BulkListSerializer
        update_lookup_field = 'name'
        partial = True


class DemandAPI(frePPleListCreateAPIView):
    queryset = freppledb.input.models.Demand.objects.all()
    serializer_class = DemandSerializer
    filter_class = DemandFilter


class DemanddetailAPI(frePPleRetrieveUpdateDestroyAPIView):
    queryset = freppledb.input.models.Demand.objects.all()
    serializer_class = DemandSerializer
