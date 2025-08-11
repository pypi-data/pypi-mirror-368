from argparse import Action
from pathlib import Path

from salute.utils.const import SCENARIO_SRC
from loguru import logger


class InitScenarioAction(Action):
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings=option_strings, dest=dest, **kwargs)
        self.path = Path().resolve()

    def __call__(self, parser, namespace, values, option_string=None):
        logger.info("Executing init scenario...")
        setattr(namespace, self.dest, True)
        self.create_scenario_folder()

    def create_scenario_folder(self):
        logger.info("Starting creating scenario...")

        scenario_folder = self.path / SCENARIO_SRC

        if scenario_folder.exists():
            logger.error("Scenario folder already exists")
            exit(1)

        try:
            scenario_folder.mkdir()
        except Exception as e:
            logger.error(f"Failed to create scenario folder: {e}")
            exit(2)

        logger.info("Scenario folder created successfully")
