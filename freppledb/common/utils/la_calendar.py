import math


def normal_calendar(start_date, work_days, week=5):
    # 休息多少天
    off_day = 7 - week
    # 当前时间为星期几,weekday()默认周一为0，周日为6，后面加1是为了保证周一从１开始
    current_time = start_date.weekday()
    current = current_time + 1
    a = week - current
    # 判断总的工作日是否大于一个星期的工作日
    if work_days > week:
        # 如果下单时间在周一到周五
        if current <= week:
            if a < work_days:
                cd = a + off_day
            else:
                cd = a
            last = work_days - a
            a = int(last / week)
            day = a * week
            lead_time = math.ceil(a * 7 + last - day)
            # 加上１是因为下单当天没有进入生产周期
            calendar_day = lead_time + cd + 1

        # 下单时间在双休
        else:
            a = 7 - current
            cd = int(work_days / week)
            day = cd * week
            lead_time = math.ceil(cd * 7 + work_days - day)
            calendar_day = lead_time + a + 1
    else:
        if work_days <= a:
            last = work_days + 1
            a = int(last / week)
            day = a * week
            calendar_day = math.ceil(a * 7 + last - day)
        else:
            calendar_day = work_days + off_day + 1

    return calendar_day

