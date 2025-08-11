from enum import StrEnum

from pydantic import BaseModel

from salute.common.models.message.payload import Payload


class Suggestion(BaseModel):
    buttons: list[dict] = []


class PronounceType(StrEnum):
    TEXT = "application/text"
    SSML = "application/ssml"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class ResponsePayload(Payload):
    pronounceText: str = ""
    pronounceTextType: PronounceType = PronounceType.TEXT
    items: list = []
    suggestions: Suggestion = Suggestion()
    auto_listening: bool = False
