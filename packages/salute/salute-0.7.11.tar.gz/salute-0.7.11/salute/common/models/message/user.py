from pydantic import BaseModel


class User(BaseModel):
    sub: str
    userChannel: str = "COMPANION_B2C"
    userId: str
