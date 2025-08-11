from decouple import config
from sanic import Config

from salute.common.models.scenario.scenario import Scenario
from salute.common.store.store import StoreProvider


class AppConfig(Config):
    STAND: str = config("STAND", default=False, cast=str)
    NAME: str = config("NAME", default=None, cast=str)
    VERSION: str = config("VERSION", default="0.0.1", cast=str)
    STORAGE: StoreProvider | None = None
    SCENARIOS: dict[str, Scenario] = {}
    APP_CONNECTOR_ROUTE: str = config(
        "APP_CONNECTOR_ROUTE", default="/app-connector", cast=str
    )


app_config = AppConfig()
