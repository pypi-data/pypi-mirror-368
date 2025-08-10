from typing import Any
from dependency_injector import containers, providers

class Container(containers.DynamicContainer):
    config: providers.Configuration = providers.Configuration()

    @staticmethod
    def from_dict(
            config: dict[str, Any],
            required: bool = False
        ) -> 'Container':
        container: Container = Container()
        container.config.from_dict(config, required)
        return container
    
    @staticmethod
    def from_json(
            file: str,
            required: bool = False,
            envs_required: bool = False
        ) -> 'Container':
        container: Container = Container()
        container.config.from_json(file, required, envs_required)
        return container