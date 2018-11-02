from datetime import datetime


def weeknum2datetime(year, week_number, first_day=1):
    """
    将第几周转换时间, 默认星期一为周第一天
    :param year:
    :param week_number:
    :param first_day: 默认 1, 星期一
    :return:
    """
    return datetime.strptime(("%s %s %s" % (year, week_number, first_day)), '%Y %W %w')


def monthnum2datetime(year, month_number):
    """
    将月数转换为
    :param year:
    :param month_number:
    :return:
    """
    return datetime.strptime(("%s %s" % (year, month_number)), '%Y %m')
