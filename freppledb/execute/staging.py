# staging唯一号
# 获取/准备参数
# 写入参数

# 加载参数
# 运算
# 写入运算结果
import traceback
from uuid import uuid1

from django.utils import timezone

from freppledb.execute.models import DataStagingLog, Task
from freppledb.input.enum import ExecuteTaskStatus


class StagingProcessor:
    def __init__(self, user=None, run_background=True, *args, **kwargs):
        self.nr = uuid1()
        self.user = user
        self.run_background = run_background
        self.parameter = {'user': user, 'run_background': run_background}
        self.init_staging_log(args, kwargs)
        if self.run_background:
            self.init_task(args, kwargs)

    def init_staging_log(self, *args, **kwargs):
        self.log = DataStagingLog()
        self.log.nr = self.nr
        self.log.input_data = self.parameter
        self.log.result = False
        self.log.create_user_nr = self.user.username if self.user else None

        self.log.created_at = self.log.updated_at = timezone.now()

    def init_task(self, *args, **kwargs):
        self.task = Task()
        self.task.name = self.__class__.__name__
        self.task.started = self.task.submitted = timezone.now()
        self.task.status = ExecuteTaskStatus.waiting.name

        self.task.user = self.user
        self.task.create_user_nr = self.user.username if self.user else None
        self.create_task()
        self.log.task = self.task

    def run(self, *args, **kwargs):
        try:
            self.log.start_at = timezone.now()
            if self.task:
                self.task.status = ExecuteTaskStatus.processing.name
                self.task.started = timezone.now()

            self.prepare_input(args, kwargs)
            self.process(args, kwargs)
            self.write_output(args, kwargs)
            self.log.result = True
            if self.task:
                self.task.finished = timezone.now()
                self.task.status = ExecuteTaskStatus.done.name

        except Exception as e:
            self.log.result = False
            self.log.message = traceback.format_exc()

            if self.task:
                self.task.message = traceback.format_exc()
                self.task.finished = timezone.now()
                self.task.status = ExecuteTaskStatus.failed.name

        self.write_log(args, kwargs)
        self.update_task(args, kwargs)

    def prepare_input(self, *args, **kwargs):
        pass

    def process(self, *args, **kwargs):
        pass

    def write_output(self, *args, **kwargs):
        pass

    def create_task(self, *args, **kwargs):
        if self.task:
            self.task.save()

    def update_task(self, *args, **kwargs):
        if self.task:
            self.task.save()

    def write_log(self, *args, **kwargs):
        self.log.save()
