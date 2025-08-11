from dependency_injector.wiring import Provide, inject
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
        self.startModule()
        print("FacadeA initialized")

    @inject
    def startModule(self,
            factory: ReporterFactory = Provide[ReporterFactoryComponent.reference],
            bridge: HardwareAbstraction = Provide[HardwareAbstractionComponent.reference],
        ) -> None:
        reporter = factory.createProduct(product="A")
        bridge.someOperation(product="A")
        bridge.otherOperation(product="B")
        print("reportProducts:", reporter.reportProducts())
        print("reportOperations:", reporter.reportOperations())
