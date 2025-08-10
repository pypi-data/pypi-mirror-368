from dependency.core import Product, product
from example.plugin.hardware.factory.interfaces import Hardware
from example.plugin.base.string import StringService, StringServiceComponent

@product(
    imports=[StringServiceComponent],
)
class HardwareB(Hardware, Product):
    def __init__(self) -> None:
        self.__string: StringService = StringServiceComponent.provide()

    def doStuff(self, operation: str) -> None:
        random_string = self.__string.getRandomString()
        print(f"HardwareB {random_string} works with operation: {operation}")