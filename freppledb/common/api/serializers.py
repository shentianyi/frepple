#
# Copyright (C) 2015-2017 by frePPLe bvba
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
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer as DefaultModelSerializer
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from rest_framework.fields import JSONField
from freppledb.common.fields import JSONBField
from rest_framework.pagination import PageNumberPagination
from rest_framework.fields import empty
import collections

DefaultModelSerializer.serializer_field_mapping[JSONBField] = JSONField

# CMARK自定义分页类
class CustomerNumberPagination(PageNumberPagination):
    #每页显示多少个
    page_size = 100
    #默认每页显示3个，可以通过传入pager1/?page=2&size=4,改变默认每页显示的个数
    page_size_query_param = "pagesize"
    #获取页码数的
    page_query_param = "page"

    #自定义分页返回
    def get_paginated_response(self, data):
      return Response({
        # 不显示上一个/下一个链接
        # 'links': {
        #   'next': self.get_next_link(),
        #   'previous': self.get_previous_link()
        # },
        # 当前页
        'page': self.page.number,
        # 每页个数
        'pagesize': self.page.paginator.per_page,
        # 总个数
        'count': self.page.paginator.count,
        # 总页数
        'total_pages': self.page.paginator.num_pages,
        # 数据
        'results': data
      })

# # CMARK 关系模型的序列化
# class RelationModelSerializer(DefaultModelSerializer):
#   def __init__(self, instance=None, data=empty, **kwargs):
#     self.is_relation = kwargs.pop('is_relation',False)
#     super(RelationModelSerializer,self).__init__(instance, data, **kwargs)
#


class ModelSerializer(DefaultModelSerializer):
  '''
  The django model serializer extends the default implementation with the
  following capabilities:
    - Ability to work with natural keys.
    - Support for create-or-update on the POST method.
      The default POST method only supports create.
      The PUT method remains update-only.
    - Enable partial updates by default
  '''
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # Cache the name of the primary key
    self.pk = self.Meta.model._meta.pk.name.lower()

    # Cache the natural key
    if hasattr(self.Meta.model.objects, 'get_by_natural_key'):
      if self.Meta.model._meta.unique_together:
        self.natural_key = self.Meta.model._meta.unique_together[0]
      elif hasattr(self.Meta.model, 'natural_key'):
        self.natural_key = self.Meta.model.natural_key
      else:
        self.natural_key = None
    else:
      self.natural_key = None

    # Strip out the uniqueness validators on primary keys.
    # We don't need them with our find-or-create feature.
    for i in self.fields:
      if i == self.pk or (self.natural_key and i in self.natural_key):
        self.fields[i].required = False

      # CMARK 去掉主键的唯一性验证, 为了更新
      if i == self.pk:
        self.fields[i].validators = [
          i for i in self.fields[i].validators
          if not isinstance(i, UniqueValidator)
          ]
      # CMARK 去掉naturalkey的唯一性验证, 为了更新
      if self.natural_key and i in self.natural_key:
        self.fields[i].validators = [
          i for i in self.fields[i].validators
          if not isinstance(i, UniqueValidator)
        ]

    # Strip out the uniqueness validators on natural keys.
    # We don't need them with our find-or-create feature.
    self.validators = [
      i for i in self.validators
      if not isinstance(i, UniqueTogetherValidator) or not i.fields == self.natural_key
      ]


  def create(self, validated_data):

    for k,v in validated_data.items():
      m=type(k)
      n=type(v)
      j=1
      if n is collections.OrderedDict:



    if self.pk in validated_data or not self.natural_key:
      # Find or create based on primary key or models without primary key
      try:
        instance = self.Meta.model.objects.using(self.context['request'].database).get(pk=validated_data[self.pk])
        return super().update(instance, validated_data)
      except self.Meta.model.DoesNotExist:
        return super().create(validated_data)
    else:
      # Find or create using natural keys
      key = []
      for x in self.natural_key:
        key.append(validated_data.get(x, None))
      # Try to find an existing record using the natural key
      try:
        instance = self.Meta.model.objects.get_by_natural_key(*key)
        return super().update(instance, validated_data)
      except self.Meta.model.DoesNotExist:
        return super().create(validated_data)
