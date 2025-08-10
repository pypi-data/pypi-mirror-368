import logging
from dependency.core.injection.base import ProviderInjection, ProviderDependency
from dependency.core.exceptions import DependencyError
logger = logging.getLogger("DependencyLoader")

def dep_in_layers(dep: ProviderInjection, layers: list[list[ProviderInjection]]) -> bool:
    return any(
        issubclass(res.provided_cls, dep.interface_cls)
        for layer in layers
        for res in layer
    )

def provider_is_resolved(dependencies: list[ProviderInjection], resolved_layers: list[list[ProviderInjection]]) -> bool:
    return all(
        dep_in_layers(dep, resolved_layers)
        for dep in dependencies
    )

def provider_unresolved(provider: ProviderDependency, resolved_layers: list[list[ProviderInjection]]) -> list[ProviderInjection]:
    dependencies = provider.imports
    return [
        dep
        for dep in dependencies
        if not dep_in_layers(dep, resolved_layers)
    ]

def provider_detect_missing(
        dependency: ProviderDependency,
        resolved_layers: list[list[ProviderInjection]]
    ) -> list[ProviderInjection]:
    deps_missing = provider_unresolved(dependency, resolved_layers)
    logger.error(f"Provider {dependency} has unresolved dependencies: {deps_missing}")
    return deps_missing

def raise_providers_error(
        providers: list[ProviderInjection],
        resolved_layers: list[list[ProviderInjection]]
    ) -> None:
    for provider in providers:
        provider_detect_missing(
            dependency=ProviderDependency(
                name=str(provider),
                imports=provider.imports),
            resolved_layers=resolved_layers)
    raise DependencyError("Dependencies cannot be resolved")

def raise_dependency_error(
        dependencies: list[ProviderDependency],
        resolved_layers: list[list[ProviderInjection]]
    ) -> None:
    for dependency in dependencies:
        provider_detect_missing(dependency, resolved_layers)
    raise DependencyError("Dependencies cannot be resolved")