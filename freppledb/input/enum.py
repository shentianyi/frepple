from enum import Enum
from django.utils.translation import ugettext_lazy as _

class BaseEnum(Enum):

    @classmethod
    def to_tuple(cls):
      return tuple((x.name,x.value,) for x in cls._member_map_.values())




class FgStatus(BaseEnum):
    S0 = _('S0')
    S1 = _('S1')
    S2 = _('S2')
    S3 = _('S3')
    S4 = _('S4')


class RmStatus(BaseEnum):
    A0 = _('A0')
    A1 = _('A1')
    A2 = _('A2')
    A3 = _('A3')


class Types(BaseEnum):
    FG = _('FG')
    WIP = _('WIP')
    RM = _('RM')




class Strategies(BaseEnum):
    MTS = _('MTS')
    MTO = _('MTO')
    ETO = _('ETO')


class LockTypes(BaseEnum):
    locked = _('locked')
    unlocked = _('unlocked')


class AbcType(BaseEnum):
    A = _('A')
    B = _('B')
    C = _('C')
    D = _('D')
