from sanic import Sanic
from sanic.logging.loggers import logger
from sanic.request import Request
from sanic.response import json, JSONResponse

from salute.common.models.message.name import Name
from salute.common.models.request_message import RequestMessage
from salute.common.models.response_message import ResponseMessage
from salute.common.models.scenario.scenario import Scenario
from salute.common.store.store import StoreProvider
from salute.plugins.use import use_plugins


class App(Sanic):
    def __init__(self, name: str, *args, **kwargs) -> None:
        super().__init__(name, *args, **kwargs)

        self._setup_plugins()
        self._setup_scenario_router()

    @staticmethod
    def _setup_plugins():
        use_plugins()

    def _setup_scenario_router(self) -> None:
        @self.post(self.config.APP_CONNECTOR_ROUTE)
        async def app_connector(request: Request) -> JSONResponse:
            logger.info("Get request message")
            data = RequestMessage(**request.json)
            logger.info("Data prepared")

            logger.info("Check root intent")
            project = data.payload.app_info.projectId
            logger.info(f"Project ID: {project}")

            scenario: Scenario | None = self.get_scenario(project)

            if scenario:
                logger.info(f"Scenario {scenario.info.name} {project} is found")
                response = await scenario.app.process(data)
                return json(response.model_dump(mode="json"), 200)

            logger.info(f"Nothing found for {project}")
            response = ResponseMessage(**data.model_dump(mode="json"))
            response.messageName = Name.NOTHING_FOUND

            return json(response.model_dump(mode="json"), 200)

    def get_storage(self) -> StoreProvider:
        return self.config.STORAGE

    def get_scenario(self, project_id: str) -> Scenario | None:
        return self.config["SCENARIOS"].get(project_id, None)
