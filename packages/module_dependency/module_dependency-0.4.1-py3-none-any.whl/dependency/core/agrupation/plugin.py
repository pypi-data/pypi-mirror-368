from abc import abstractmethod
from pydantic import BaseModel
from dependency.core.agrupation.module import Module
from dependency.core.injection.base import ProviderInjection
from dependency.core.injection.container import Container

class PluginMeta(BaseModel):
    name: str
    version: str

    def __str__(self) -> str:
        return f"Plugin {self.name} {self.version}"

class Plugin(Module):
    meta: PluginMeta
    container: Container

    @property
    @abstractmethod
    def config(self) -> BaseModel:
        pass

    def resolve_providers(self, container: Container) -> list[ProviderInjection]:
        self.container = container
        setattr(container, self.injection.name, self.injection.inject_cls())
        return [provider for provider in self.injection.resolve_providers()]

    def __repr__(self):
        return f"{self.meta}: {self.config}"