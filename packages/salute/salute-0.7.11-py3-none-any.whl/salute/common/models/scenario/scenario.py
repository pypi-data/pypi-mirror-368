from pydantic import BaseModel
from salute.common.models.scenario.scenario_app import ScenarioApp, SessionStore
from salute.common.models.scenario.utils import ScenarioInfo


class Scenario(BaseModel):
    app: ScenarioApp
    info: ScenarioInfo
    session_store: SessionStore

    class Config:
        arbitrary_types_allowed = True
