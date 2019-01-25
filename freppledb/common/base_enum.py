from enum import Enum
from django.utils.translation import ugettext_lazy as _


class BaseEnum(Enum):

    @classmethod
    def to_tuple(cls):
        # return tuple((x.name, x.value,) for x in filter(lambda x:type(x.value)!=tuple, cls._member_map_.values()))
        return tuple((x.name, x.value,) for x in cls._member_map_.values())

    @classmethod
    def to_dic(cls):
        # return dict((x.name, x.value,) for x in filter(lambda x:type(x.value)!=tuple,cls._member_map_.values()))

        return dict((x.name, x.value,) for x in cls._member_map_.values())
