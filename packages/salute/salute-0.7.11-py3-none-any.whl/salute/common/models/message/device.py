from pydantic import BaseModel


class Device(BaseModel):
    additionalInfo: dict = {}
    capabilities: dict = {}
    deviceId: str = ""
    deviceManufacturer: str = ""
    deviceModel: str = ""
    features: dict = {}
    platformType: str = ""
    platformVersion: str = ""
    surface: str = ""
    surfaceVersion: str = ""
