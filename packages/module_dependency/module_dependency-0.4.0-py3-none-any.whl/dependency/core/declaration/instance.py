from typing import Callable, cast
from dependency_injector import providers
from dependency.core.declaration.base import ABCInstance
from dependency.core.declaration.component import Component
from dependency.core.declaration.product import Product

class Instance(ABCInstance):
    """Instance Base Class
    """
    def __init__(self, provided_cls: type):
        super().__init__(provided_cls=provided_cls)

def instance(
        component: type[Component],
        imports: list[type[Component]] = [],
        products: list[type[Product]] = [],
        provider: type[providers.Provider] = providers.Singleton,
        bootstrap: bool = False,
    ) -> Callable[[type], Instance]:
    """Decorator for instance class

    Args:
        component (type[Component]): Component class to be used as a base class for the provider.
        imports (list[type[Component]], optional): List of components to be imported by the provider. Defaults to [].
        products (list[type[Product]], optional): List of products to be declared by the provider. Defaults to [].
        provider (type[providers.Provider], optional): Provider class to be used. Defaults to providers.Singleton.
        bootstrap (bool, optional): Whether the provider should be bootstrapped. Defaults to False.
        
    Raises:
        TypeError: If the wrapped class is not a subclass of Component declared base class.

    Returns:
        Callable[[type], Instance]: Decorator function that wraps the instance class and returns an Instance object.
    """
    # Cast due to mypy not supporting class decorators
    _component = cast(Component, component)
    _imports = cast(list[Component], imports)
    _products = cast(list[Product], products)
    def wrap(cls: type) -> Instance:
        if not issubclass(cls, _component.interface_cls):
            raise TypeError(f"Class {cls} is not a subclass of {_component.interface_cls}")

        imports = [component.injection for component in _imports]
        depends = [product._dependency_imports for product in _products]
        _component.injection.set_implementation(
            provided_cls=cls,
            provider_cls=provider,
            component_cls=_component.__class__,
            imports=imports,
            depends=depends,
            bootstrap=_component.provide if bootstrap else None)
        
        instance = Instance(
            provided_cls=cls)
        _component.instance = instance
        return instance
    return wrap