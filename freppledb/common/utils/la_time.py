import calendar
from datetime import datetime

from dateutil.relativedelta import relativedelta


def ios_weeknumberstr(dt):
    """
    返回周数字符串,如01..53,使用%V,
    2019-1-1 使用%W是0周,使用%V是1周,
    :param dt:
    :return:
    """
    return dt.strftime('%V')


# 周是1-53周, 但是程序中从0开始
def weeknum2dt(year, week_number, first_day=1):
    """
    将第几周转换时间, 默认星期一为周第一天, week_number从1开始
    :param year:
    :param week_number:
    :param first_day: 默认 1, 星期一
    :return:
    """
    # return datetime.strptime(("%s %s %s" % (year, week_number, first_day)),
    #                          '%Y %W %w')

    return datetime.strptime(("%s %s %s" % (year, week_number, first_day)),
                             '%G %V %w')

def dt2weekdt(dt, first_day=1):
    """
    获取当前时间的周.第一天
    :param datetime:
    :param first_day:
    :return:
    """
    return weeknum2dt(dt.year, dt.strftime('%V'), first_day)


def dt2lastweekdt(dt, first_day=1):
    return dt2weekdt(dt, first_day) + relativedelta(days=6)


def monthnum2dt(year, month_number):
    """
    将月数转换为
    :param year:
    :param month_number:
    :return:
    """
    return datetime.strptime(("%s %s" % (year, month_number)), '%Y %m')


def dt2monthdt(dt):
    """
    获取当前时间的月, 第一天
    :param datetime:
    :return:
    """
    return monthnum2dt(dt.year, dt.month)


def string2dt(str, format="%Y-%m-%d %H:%M:%S"):
    """
    字符串转换为datetime
    :param str:
    :param format:
    :return:
    """
    return datetime.strptime(str, format)


def dt2string(dt, format="%Y-%m-%d %H:%M:%S"):
    """
    datetime转换为字符串
    :param datetime:
    :param format:
    :return:
    """
    return datetime.strftime(dt, format)


def week_search_starttime(dt):
    dt = dt2weekdt(dt)
    return datetime(dt.year, dt.month, dt.day)


def week_search_endtime(dt):
    dt = dt2lastweekdt(dt)
    return datetime(dt.year, dt.month, dt.day, 23, 59, 59, 999999)


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
                    999999)


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


def last_n_year_time(dt, n=1):
    """
    获取N年前的时间, n默认1
    :param dt:
    :param n:
    :return:
    """
    return dt + relativedelta(years=-n)


def next_n_year_time(dt, n=1):
    """
    获取N年后的时间, n默认1
    :param dt:
    :param n:
    :return:
    """
    return dt + relativedelta(years=n)
