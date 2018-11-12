import calendar
from datetime import datetime


def weeknum2dt(year, week_number, first_day=1):
    """
    将第几周转换时间, 默认星期一为周第一天
    :param year:
    :param week_number:
    :param first_day: 默认 1, 星期一
    :return:
    """
    return datetime.strptime(("%s %s %s" % (year, week_number, first_day)), '%Y %W %w')


def monthnum2dt(year, month_number):
    """
    将月数转换为
    :param year:
    :param month_number:
    :return:
    """
    return datetime.strptime(("%s %s" % (year, month_number)), '%Y %m')


def month_search_starttime(dt):
    """
    获取本月的搜索开始时间
    :param dt:
    :return:
    """
    return datetime(dt.year, dt.month, 1)



def month_search_endtime(dt):
    """
      获取本月的搜索结束时间
      :param dt:
      :return:
      """
    return datetime(dt.year, dt.month, calendar.monthrange(dt.year, dt.month)[1], 23, 59,
                    59,
                    999)



def last_month_time(dt):
    """
    获取上个月时间, 如2018-01-01 00:00:00
    :param dt:
    :return:
    """
    return datetime(dt.year - 1, 1, 1) if dt.month == 1 else datetime(dt.year,
                                                                      dt.month - 1, 1)


def next_month_time(dt):
    """
    获取下个月时间, 如2018-01-01 00:00:00
    :param dt:
    :return:
    """
    return datetime(dt.year + 1, 1, 1) if dt.month == 12 else datetime(dt.year, dt.month + 1, 1)
