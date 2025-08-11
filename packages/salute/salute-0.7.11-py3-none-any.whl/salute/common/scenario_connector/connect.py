import importlib
from pathlib import Path
from sanic.logging.loggers import logger


SPECIAL_DIRS = ["__pycache__", ".git"]


class ScenarioConnector:
    SCENARIO_SRC = "scenarios"
    SCENARIO_CONNECT_METHOD = "scenario_connector"

    def __init__(self):
        p = Path().resolve()
        self.scenarios_dirs = p / self.SCENARIO_SRC

    async def connect(self) -> None:
        connected_count = 0

        for full_path in self.scenarios_dirs.iterdir():
            directory = full_path.parts[len(full_path.parts) - 1]

            if not full_path.is_dir() or directory in SPECIAL_DIRS:
                continue

            logger.info(f"Connecting to scenario {directory}")

            try:
                mod = importlib.import_module(f"{self.SCENARIO_SRC}.{directory}")
                process = getattr(mod, self.SCENARIO_CONNECT_METHOD)
                await process(full_path)
                connected_count += 1
                logger.info(f"Scenario {directory} is connected")
            except Exception as e:
                logger.error(f"Failed to connect to scenario {directory}: {e}")

        logger.info(f"Total {connected_count} scenarios connected")
