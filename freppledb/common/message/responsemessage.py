from django.core.serializers.python import Serializer


class ResponseMessage:
    result = False
    message = None
    content = None

    def __init__(self, result=False, message=None, content=None):
        self.result = result
        self.message = message
        self.content = content

# class ResponseMessageSerializer(Serializer):
#     def end_object(self, obj):
#
#
#
#     class Meta:
#         model = ResponseMessage
#         fields = ('result', 'message')
