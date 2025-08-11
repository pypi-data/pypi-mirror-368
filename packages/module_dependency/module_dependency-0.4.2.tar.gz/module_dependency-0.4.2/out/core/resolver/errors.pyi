from _typeshed import Incomplete
from dependency.core.declaration import Component as Component
from dependency.core.declaration.provider import Provider as Provider

logger: Incomplete

def provider_detect_error(provider: Provider, unresolved_providers: list[Provider], resolved_layers: list[list[Provider]]) -> tuple[list[Component], list[Component]]: ...
def raise_dependency_error(providers: list[Provider], resolved_layers: list[list[Provider]]) -> None: ...
