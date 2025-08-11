from pydantic import BaseModel

from salute.common.models.message.device import Device


class Payload(BaseModel):
    intent: str
    device: Device
