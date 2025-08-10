from dependency.core import Product, product
from example.plugin.hardware.factory.interfaces import Hardware
from example.plugin.base.number import NumberService, NumberServiceComponent

@product(
    imports=[NumberServiceComponent],
)
class HardwareA(Hardware, Product):
    def __init__(self) -> None:
        self.__number: NumberService = NumberServiceComponent.provide()

    def doStuff(self, operation: str) -> None:
        random_number = self.__number.getRandomNumber()
        print(f"HardwareA {random_number} works with operation: {operation}")