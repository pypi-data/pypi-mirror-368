from dependency.core import instance, providers
from example.plugin.base.number import NumberService, NumberServiceComponent

@instance(
    component=NumberServiceComponent,
    provider=providers.Singleton
)
class FakeNumberService(NumberService):
    def getRandomNumber(self) -> int:
        return 42