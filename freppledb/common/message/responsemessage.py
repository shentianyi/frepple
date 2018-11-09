from django.core.serializers.python import Serializer


class ResponseMessage:
    result = False
    code = 200
    message = None
    content = None

    def __init__(self, result=False,code=200, message=None, content=None):
        self.result = result
        self.code = code
        self.message = message
        self.content = content
