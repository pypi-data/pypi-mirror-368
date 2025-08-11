from importlib.metadata import entry_points
from sanic.log import logger


def use_plugins():
    discovered_plugins = entry_points(group="salute.plugins")
    logger.info("Initializing plugins")

    for plugin in discovered_plugins:
        logger.info(f"Loading {plugin.name}")

        try:
            current_plugin = plugin.load()
            current_plugin()

            logger.info(f"Plugin {plugin.name} successfully loaded")

        except Exception as e:
            logger.error(f"Failed to load plugin {plugin.name}: {e}")
