from salute.common.models.message.app_info import AppInfo
from salute.common.models.message.payload import Payload
from salute.common.models.message.text import Text


class RequestPayload(Payload):
    app_info: AppInfo
    message: Text
