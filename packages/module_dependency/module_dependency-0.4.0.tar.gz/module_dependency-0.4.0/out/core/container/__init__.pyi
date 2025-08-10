from dependency_injector import containers, providers
from typing import Any

class Container(containers.DynamicContainer):
    config: providers.Configuration
    @staticmethod
    def from_dict(config: dict[str, Any], required: bool = False) -> Container: ...
    @staticmethod
    def from_json(file: str, required: bool = False, envs_required: bool = False) -> Container: ...
