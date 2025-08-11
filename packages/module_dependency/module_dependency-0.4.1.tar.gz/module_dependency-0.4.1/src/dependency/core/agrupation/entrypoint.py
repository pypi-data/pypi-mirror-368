import time
import logging
from typing import cast
from dependency.core.agrupation.plugin import Plugin
from dependency.core.injection.container import Container
from dependency.core.injection.loader import InjectionLoader

logger = logging.getLogger("DependencyLoader")
init_time = time.time()

class Entrypoint():
    def __init__(self, container: Container, plugins: list[type[Plugin]]) -> None:
        # Cast due to mypy not supporting class decorators
        _plugins = cast(list[Plugin], plugins)
        providers = [
            provider
            for plugin in _plugins
            for provider in plugin.resolve_providers(container)]

        self.loader = InjectionLoader(
            container=container,
            providers=providers)
        self.loader.resolve_dependencies()
        logger.info(f"Application started in {time.time() - init_time} seconds")