import logging
from pprint import pformat
from dependency.core.injection.base import ProviderInjection
from dependency.core.injection.container import Container
from dependency.core.injection.utils import (
    provider_is_resolved,
    raise_providers_error,
    raise_dependency_error,
)
logger = logging.getLogger("DependencyLoader")

class InjectionLoader:
    def __init__(self, container: Container, providers: list[ProviderInjection]) -> None:
        self.container: Container = container
        self.providers: list[ProviderInjection] = providers

    def resolve_dependencies(self) -> list[list[ProviderInjection]]:
        unresolved_providers: list[ProviderInjection] = self.providers
        resolved_layers: list[list[ProviderInjection]] = []

        while unresolved_providers:
            new_layer = [
                provider
                for provider in unresolved_providers
                if provider_is_resolved(provider.imports, resolved_layers)
            ]

            if len(new_layer) == 0:
                raise_providers_error(unresolved_providers, resolved_layers)
            resolved_layers.append(new_layer)

            unresolved_providers = [
                provider
                for provider in unresolved_providers
                if provider not in new_layer
            ]
        named_layers = pformat(resolved_layers)
        logger.info(f"Resolved layers:\n{named_layers}")

        unresolved_depends = [
            depends
            for provider in self.providers
            for depends in provider.depends
            if not provider_is_resolved(depends.imports, resolved_layers)]
        if unresolved_depends:
            logger.error(f"Unresolved dependencies: {unresolved_depends}")
            raise_dependency_error(unresolved_depends, resolved_layers)

        self.container.check_dependencies()
        self.container.init_resources()

        for resolved_layer in resolved_layers:
            for provider in resolved_layer:
                provider.do_bootstrap(self.container)
        
        logger.info("Dependencies resolved and injected")
        return resolved_layers