import logging
from dependency.core.injection.base import ProviderInjection, ProviderDependency
from dependency.core.exceptions import DependencyError
logger = logging.getLogger("DependencyLoader")

def dep_in_layers(provider: ProviderInjection, layers: list[list[ProviderInjection]]) -> bool:
    return any(
        issubclass(res.provided_cls, provider.interface_cls)
        for layer in layers
        for res in layer
    )

def provider_is_resolved(dependency: ProviderDependency, resolved_layers: list[list[ProviderInjection]]) -> bool:
    return all(
        dep_in_layers(provider, resolved_layers)
        for provider in dependency.imports
    )

def provider_unresolved(dependency: ProviderDependency, resolved_layers: list[list[ProviderInjection]]) -> list[ProviderInjection]:
    return [
        provider
        for provider in dependency.imports
        if not dep_in_layers(provider, resolved_layers)
    ]

class Cycle():
    def __init__(self, elements: list[ProviderInjection]) -> None:
        self.elements = self.normalize(elements)
    
    @staticmethod
    def normalize(cycle: list[ProviderInjection]) -> tuple[str, ...]:
        # Rota el ciclo para que el menor (por str) esté primero, para comparar fácilmente
        min_idx = min(range(len(cycle)), key=lambda i: str(cycle[i]))
        normalized = cycle[min_idx:] + cycle[:min_idx] + [cycle[min_idx]]
        return tuple(str(p) for p in normalized)

    def __hash__(self) -> int:
        return hash(self.elements)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Cycle):
            return False
        return self.elements == other.elements

    def __repr__(self) -> str:
        return ' -> '.join(str(p) for p in self.elements)

def find_cycles(providers: list[ProviderInjection]) -> set[Cycle]:
    """Detect unique cycles in the dependency graph.
       Returns a set of cycles, each represented as a Cycle object.
    """
    cycles: set[Cycle] = set()

    def visit(node: ProviderInjection, path: list[ProviderInjection], visited: set[ProviderInjection]) -> None:
        if node in path:
            cycle_start = path.index(node)
            cycle = Cycle(path[cycle_start:])
            if cycle not in cycles:
                cycles.add(cycle)
            return
        if node in visited:
            return
        visited.add(node)
        for dep in node.imports:
            visit(dep, path + [node], visited)

    for provider in providers:
        visit(provider, [], set())
    return cycles

def raise_cycle_error(providers: list[ProviderInjection]) -> None:
    cycles = find_cycles(providers)
    if cycles:
        for cycle in cycles:
            logger.error(f"Circular import: {cycle}")
        raise DependencyError("Circular dependencies detected")

def raise_dependency_error(
        dependencies: list[ProviderDependency],
        resolved_layers: list[list[ProviderInjection]],
    ) -> None:
    for dependency in dependencies:
        unresolved = provider_unresolved(dependency, resolved_layers)
        logger.error(f"Provider {dependency} has unresolved dependencies: {unresolved}")
    raise DependencyError("Providers cannot be resolved")

def raise_providers_error(
        providers: list[ProviderInjection],
        resolved_layers: list[list[ProviderInjection]],
    ) -> None:
    raise_cycle_error(providers)
    raise_dependency_error(
        dependencies=[
            provider.dependency
            for provider in providers],
        resolved_layers=resolved_layers)