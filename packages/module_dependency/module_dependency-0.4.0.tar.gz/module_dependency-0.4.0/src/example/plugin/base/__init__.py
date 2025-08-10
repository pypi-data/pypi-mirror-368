from dependency.core import Plugin, PluginMeta, module
from example.plugin.base.settings import BasePluginConfig

@module()
class BasePlugin(Plugin):
    meta = PluginMeta(name="BasePlugin", version="0.1.0")

    @property
    def config(self) -> BasePluginConfig:
        return BasePluginConfig(**self.container.config())