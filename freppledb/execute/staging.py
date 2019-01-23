# staging唯一号
# 获取/准备参数
# 写入参数

# 加载参数
# 运算
# 写入运算结果
from uuid import uuid1

from django.utils import timezone

from freppledb.execute.models import DataStagingLog


class StagingProcessor:
    def __init__(self, user_nr=None, *args, **kwargs):
        self.nr = uuid1()

        self.log = DataStagingLog()
        self.log.nr = self.nr
        self.log.input = {'parameter': self.parameter}
        self.log.result = False
        self.log.create_user_nr = user_nr
        self.log.start_at = log.created_at = log.updated_at = timezone.now()

    def run(self):
        try:
            self.prepare_input()
            self.process()
            self.write_output()
            self.log.result = True
        except Exception as e:
            self.log.result = False
            self.log.message = e

        self.write_log()

    def prepare_input(self):
        pass

    def process(self):
        pass

    def write_output(self):
        pass

    def write_log(self):
        self.log.save()
