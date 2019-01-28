from freppledb.common.models import Bucket


def create_point(start_time, end_time,date_type,rows):
    """
    :param start_time: 开始时间
    :param end_time: 结束时间
    :param date_type: 日期
    :param rows: 查询集
    :return:
    """
    point_list = []
    while start_time <= end_time:
        points = {
            "x_value": start_time,
            "x_text": Bucket.get_x_text_name(start_time, date_type),
            "y": 0
        }
        qty = 0
        for i in rows:
            if start_time == i.parsed_date:
                qty = i.qty
        points["y"] = qty
        point_list.append(points)
        start_time = Bucket.get_nex_time_by_date_type(start_time, date_type)
    return point_list
