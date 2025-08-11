from enum import Enum


class Name(str, Enum):
    MESSAGE_TO_SKILL = "MESSAGE_TO_SKILL"
    CLOSE_APP = "CLOSE_APP"
    RUN_APP = "RUN_APP"
    ERROR = "ERROR"
    NOTHING_FOUND = "NOTHING_FOUND"
    ANSWER_TO_USER = "ANSWER_TO_USER"
