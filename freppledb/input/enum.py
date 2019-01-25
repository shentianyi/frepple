from django.utils.translation import ugettext_lazy as _

from freppledb.common.base_enum import BaseEnum


class FgStatus(BaseEnum):
    """
    物料状态-FG
    """
    S0 = _('S0')
    S1 = _('S1')
    S2 = _('S2')
    S3 = _('S3')
    S4 = _('S4')


class RmStatus(BaseEnum):
    """
    物料状态-RM
    """
    A0 = _('A0')
    A1 = _('A1')
    A2 = _('A2')
    A3 = _('A3')


class ItemStatus(BaseEnum):
    """物料状态"""
    S0 = _('S0')
    S1 = _('S1')
    S2 = _('S2')
    S3 = _('S3')
    S4 = _('S4')
    A0 = _('A0')
    A1 = _('A1')
    A2 = _('A2')
    A3 = _('A3')


class ItemType(BaseEnum):
    """物料类型"""
    FG = _('FG')
    WIP = _('WIP')
    RM = _('RM')


class DeliveryOrderType(BaseEnum):
    outbound = _('outbound')
    inbound = _('inbound')
    other = _('other')


class DeliveryOrderStatus(BaseEnum):
    open = _('open')
    git = _('git')
    partially_delivered = _('partially delivered')
    fully_delivered = _('fully delivered')
    rejected = _('rejected')
    canceled = _('canceled')


class SalesOrderStatus(BaseEnum):
    open = _('open')
    closed = _('closed')
    canceled = _('canceled')
    invoiced = _('invoiced')


class RelationType(BaseEnum):
    """物料替代关系类型"""
    successor = _('successor')
    replacement = _('replacement')


class ItemTypeStatus(BaseEnum):
    """物料类型状态关系"""
    FG = FgStatus.to_tuple()
    RM = RmStatus.to_tuple()
    WIP = ()

class ItemProductStrategy(BaseEnum):
    """物料计划策略"""
    MTS = _('MTS')
    MTO = _('MTO')
    ETO = _('ETO')


class LockType(BaseEnum):
    """物料锁定类型"""
    locked = _('locked')
    unlocked = _('unlocked')


class AbcType(BaseEnum):
    """物料ABC"""
    A = _('A')
    B = _('B')
    C = _('C')
    D = _('D')


class CommonType(BaseEnum):
    """资源类型"""
    default = _('default')
    infinite = _('infinite')


class OperationType(BaseEnum):
    """工序类型"""
    fixed_time = _('fixed_time')
    time_per = _('time_per')
    alternate = _('alternate')
    split = _('split')
    routing = _('routing')


class OperationMode(BaseEnum):
    """备选工序选择模式"""
    priority = _('priority')
    mincost = _('mincost')


class MaterialType(BaseEnum):
    """工序物料类型"""
    start = _('Start')
    end = _('End')


class ForecastCommentStatus(BaseEnum):
    """预测版本状态"""
    init = _('forecast init')
    ok = _('forecast ok')
    nok = _('forecast nok')
    cancel = _('forecast cancel')
    release = _('forecast release')
    confirm = _('forecast confirm')

    CAN_CALCULATE_MDS_STATUS = ('confirm',)


class ForecastDateType(BaseEnum):
    """预测时间类型"""
    W = _('W')
    M = _('M')


class ParameterValueType(BaseEnum):
    string = _('string')
    int = _('int')
    number = _('number')
    datetime = _('datetime')


class ExecuteTaskStatus(BaseEnum):
    waiting = _('waiting')
    processing = _('processing')
    done = _('done')
    failed = _('failed')


class DemandStatus(BaseEnum):
    """需求状态"""
    init = _('init')
    open =_('open')
    release = _('release')
    closed = _('closed')
    canceled = _('canceled')


class DemandRequestVersionStatus(BaseEnum):
    """需求请求版本状态"""
    init = _('init')
    canceled = _('canceled')
    release = _('release')
    closed = _('closed')

class DemandRequestType(BaseEnum):
    """需求请求类型"""
    manufacture = _('manufacture')
    purchase = _('purchase')


class DemandRequestStatus(BaseEnum):
    """需求请求状态"""
    init = _('init')
    canceled = _('canceled')
    release = _('release')
    closed = _('closed')



class WorkOrderStatus(BaseEnum):
    """生产工单状态"""
    init = _('init')
    open =_('open')
    closed = _('closed')
    canceled = _('canceled')
