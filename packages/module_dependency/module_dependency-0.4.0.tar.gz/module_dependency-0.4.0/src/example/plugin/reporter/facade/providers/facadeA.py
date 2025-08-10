from dependency.core import instance, providers
from example.plugin.reporter.facade import ReportFacade, ReportFacadeComponent
from example.plugin.reporter.factory import ReporterFactory, ReporterFactoryComponent
from example.plugin.hardware.bridge import HardwareAbstraction, HardwareAbstractionComponent

@instance(
    component=ReportFacadeComponent,
    imports=[
        ReporterFactoryComponent,
        HardwareAbstractionComponent
    ],
    provider = providers.Singleton,
    bootstrap=True,
)
class ReporterFacadeA(ReportFacade):
    def __init__(self) -> None:
        self.__factory: ReporterFactory = ReporterFactoryComponent.provide()
        self.__bridge: HardwareAbstraction = HardwareAbstractionComponent.provide()
        
        self.startModule()
        print("FacadeA initialized")

    def startModule(self) -> None:
        reporter = self.__factory.createProduct(product="A")
        self.__bridge.someOperation(product="A")
        self.__bridge.otherOperation(product="B")
        print("reportProducts:", reporter.reportProducts())
        print("reportOperations:", reporter.reportOperations())
