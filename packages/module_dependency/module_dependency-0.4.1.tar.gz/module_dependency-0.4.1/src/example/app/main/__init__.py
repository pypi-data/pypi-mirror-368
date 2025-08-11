import time
import logging
from dependency.core import Entrypoint, Container
from example.plugin.base import BasePlugin
from example.plugin.hardware import HardwarePlugin
from example.plugin.reporter import ReporterPlugin

logger = logging.getLogger("root")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

class MainApplication(Entrypoint):
    def __init__(self) -> None:
        # This import will load all providers
        import example.app.main.imports
        
        container = Container.from_dict(config={"config": True}, required=True)
        super().__init__(
            container,
            plugins=[
                BasePlugin,
                HardwarePlugin,
                ReporterPlugin,
            ])

    def main_loop(self) -> None:
        while True:
            time.sleep(1)