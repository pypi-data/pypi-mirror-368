from dependency_injector.wiring import Provide, inject
from dependency.core import Product, product
from example.plugin.hardware.factory.interfaces import Hardware
from example.plugin.base.number import NumberService, NumberServiceComponent

@product(
    imports=[
        NumberServiceComponent,
    ],
)
class HardwareA(Hardware, Product):
    @inject
    def doStuff(self,
            operation: str,
            number: NumberService = Provide[NumberServiceComponent.reference],
        ) -> None:
        random_number = number.getRandomNumber()
        print(f"HardwareA {random_number} works with operation: {operation}")