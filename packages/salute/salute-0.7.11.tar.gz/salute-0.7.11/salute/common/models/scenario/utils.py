from enum import Enum

from pydantic import BaseModel


class ScenarioType(str, Enum):
    CHAT_APP = "CHAT_APP"


class ScenarioInfo(BaseModel):
    key: str
    name: str
    code: str
    version: str
    type: ScenarioType
    payload: dict
