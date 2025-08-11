from pydantic import BaseModel


class AppInfo(BaseModel):
    projectId: str
    applicationId: str
    appversionId: str
    systemName: str
    projectName: str
    frontendType: str
    ageLimit: int
    affiliationType: str
