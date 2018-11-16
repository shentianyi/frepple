import math
from datetime import datetime


def tuple2select(tuple, blankable=False):
    if blankable == True:
        adict = dict(tuple)
        adict[''] = ''
        return [{"value": k, "text": v} for k, v in adict.items()]
    else:
        return [{"value": k, "text": v} for k, v in dict(tuple).items()]


def lead_time(totall_time, workday=5):

    # # 从数据库取出来的值可能为None,为None时相加减会报错
    # if receive_time is None:
    #     receive_time = 0
    # if load_time is None:
    #     load_time = 0
    # if transit_time is None:
    #     transit_time = 0
    # if product_time is None:
    #     product_time = 0

    now_time = datetime.now()
    # 按工作日计算前置期时间
    # totall_time = receive_time + load_time + transit_time + product_time
    # 休息多少天
    off_day = 7 - workday
    # 当前时间为星期几,weekday()默认周一为0，周日为6，后面加1是为了保证周一从１开始
    current_time = now_time.weekday()
    current = current_time + 1
    a = workday - current
    # 判断总的工作日是否大于一个星期的工作日
    if totall_time > workday:
        # 如果下单时间在周一到周五
        if current <= workday:
            if a < totall_time:
                cd = a + off_day
            else:
                cd = a
            last = totall_time - a
            a = int(last / workday)
            day = a * workday
            lead_time = math.ceil(a * 7 + last - day)
            # 加上１是因为下单当天没有进入生产周期
            calendar_day = lead_time + cd + 1

        # 下单时间在双休
        else:
            a = 7 - current
            cd = int(totall_time / workday)
            day = cd * workday
            lead_time = math.ceil(cd * 7 + totall_time - day)
            calendar_day = lead_time + a + 1
    else:
        if totall_time <= a:
            last = totall_time + 1
            a = int(last / workday)
            day = a * workday
            calendar_day = math.ceil(a * 7 + last - day)
        else:
            calendar_day = totall_time + off_day + 1

    return calendar_day
