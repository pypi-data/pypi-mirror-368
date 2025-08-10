from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from dependency.core.injection import ContainerInjection, ProviderInjection

TEST_REFERENCE = "container1.container2.provider1"

class Instance:
    def test(self) -> str:
        return "Test method called"

class Interface:
    @inject
    def test(self, service: Instance = Provide[TEST_REFERENCE]) -> str:
        return f"Injected service: {service.test()}"

def test_injection1():
    container1 = ContainerInjection(name="container1")
    container2 = ContainerInjection(name="container2", parent=container1)
    provider1 = ProviderInjection(
        name="provider1",
        interface_cls=Interface,
        parent=container2)
    provider1.set_implementation(
        provided_cls=Instance,
        provider_cls=providers.Singleton,
        component_cls=Interface)
    assert provider1.reference == TEST_REFERENCE

    container = containers.DynamicContainer()
    setattr(container, container1.name, container1.inject_cls())
    for provider in list(container1.resolve_providers()):
        provider.do_bootstrap(container)
    assert Interface().test() == "Injected service: Test method called"