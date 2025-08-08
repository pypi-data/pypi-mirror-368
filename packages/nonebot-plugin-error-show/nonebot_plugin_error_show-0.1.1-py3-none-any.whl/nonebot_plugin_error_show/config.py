from pathlib import Path

from nonebot import get_driver, get_plugin_config, require
from pydantic import BaseModel

require("nonebot_plugin_localstore")

import nonebot_plugin_localstore as localstore


class Config(BaseModel):
    e_bot_link: str | None = None  # BOT 好友链接
    e_bot_group_link: str | None = None  # BOT 用户交流群链接

# 配置加载
plugin_config: Config = get_plugin_config(Config)
global_config = get_driver().config

# 全局名称
NICKNAME: str = next(iter(global_config.nickname), None)

# Data目录
DATA_DIR = localstore.get_plugin_data_dir()
PLUGIN_PATH = Path(__file__).resolve().parent
