from pydantic import BaseModel

from salute.common.models.message.payload import Payload
from salute.common.models.message.user import User
from salute.common.models.message.name import Name


class Message(BaseModel):
    sessionId: str
    messageId: int
    messageName: Name
    payload: Payload
    uuid: User
