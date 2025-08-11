from dependency_injector.wiring import Provide, inject
from dependency.core import Product, product
from example.plugin.hardware.factory.interfaces import Hardware
from example.plugin.base.string import StringService, StringServiceComponent

@product(
    imports=[
        StringServiceComponent,
    ],
)
class HardwareB(Hardware, Product):
    @inject
    def doStuff(self,
            operation: str,
            string: StringService = Provide[StringServiceComponent.reference],
        ) -> None:
        random_string = string.getRandomString()
        print(f"HardwareB {random_string} works with operation: {operation}")