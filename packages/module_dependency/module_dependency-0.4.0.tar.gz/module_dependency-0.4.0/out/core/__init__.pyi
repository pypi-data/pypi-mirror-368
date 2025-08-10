from dependency.core.declaration.component import Component as Component, component as component
from dependency.core.declaration.dependent import Dependent as Dependent, dependent as dependent
from dependency.core.declaration.provider import HasDependent as HasDependent, Provider as Provider, provider as provider
from dependency.core.module.base import Module as Module, module as module
from dependency_injector import providers as providers

__all__ = ['providers', 'Module', 'module', 'Component', 'component', 'Provider', 'provider', 'Dependent', 'dependent', 'HasDependent']
