from salute.common.models.message.message import Message
from salute.common.models.message.response_payload import ResponsePayload


class ResponseMessage(Message):
    payload: ResponsePayload
