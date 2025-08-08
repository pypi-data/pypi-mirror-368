from nonebot.plugin import PluginMetadata, inherit_supported_adapters

from . import __main__ as __main__
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="自动报错",
    description="nonebot报错输出插件",
    usage="自动输出报错",
    type="application",
    homepage="https://github.com/zifox666/nonebot-plugin-error-show",
    config=Config,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={"author": "zifox666 <zifox666@mail.com>"},
)
