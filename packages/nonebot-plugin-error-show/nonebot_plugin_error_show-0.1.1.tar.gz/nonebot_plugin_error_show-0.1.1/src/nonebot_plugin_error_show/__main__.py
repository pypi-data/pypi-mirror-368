from nonebot import logger, require
from nonebot.adapters import Bot, Event
from nonebot.message import run_postprocessor
from nonebot.permission import SuperUser

from .db import TraceLogOper, TraceSubOper

require("nonebot_plugin_alconna")
require("nonebot_plugin_orm")
require("nonebot_plugin_uninfo")

from arclet.alconna import Alconna, Args, Subcommand
from nonebot_plugin_alconna import on_alconna
from nonebot_plugin_orm import async_scoped_session
from nonebot_plugin_uninfo import Uninfo

from .handle import handle_error


async def is_superuser(bot: Bot, event: Event) -> bool:
    return await SuperUser()(bot, event)


@run_postprocessor
async def handle_exception(bot: Bot, event: Event, exception: Exception | None):
    if exception:
        trace_id = await handle_error(bot, event, exception)
        logger.info(
            f"[{trace_id}]错误日志{'已发送' if trace_id else '未发送'}\n"
            f"{event}"
        )


test_error = on_alconna(
    Alconna("test_error"),
    rule=is_superuser,
    use_cmd_start=True
)
sub_error = on_alconna(
    Alconna(
        "sub_error",
        Subcommand("remove|r")
    ),
    rule=is_superuser,
    use_cmd_start=True,
)
get_error = on_alconna(
    Alconna(
        "get_error",
        Args["trace_id", str],
    ),
    rule=is_superuser,
    use_cmd_start=True,
)


@test_error.handle()
async def _():
    1 / 0


@sub_error.assign("$main")
async def error_sub_add(session: async_scoped_session, user_info: Uninfo):
    result = await TraceSubOper(session, user_info).add()
    if result:
        await sub_error.finish("异常追踪订阅添加成功")
    else:
        await sub_error.finish("异常追踪订阅添加失败")


@sub_error.assign("remove")
async def error_sub_sub(session: async_scoped_session, user_info: Uninfo):
    result = await TraceSubOper(session, user_info).delete()
    if result:
        await sub_error.finish("异常追踪订阅删除成功")
    else:
        await sub_error.finish("异常追踪订阅删除失败")


@get_error.handle()
async def _(session: async_scoped_session, trace_id: str):
    trace_log = await TraceLogOper(session=session, uuid_str=trace_id).get()
    if trace_log:
        await get_error.finish(f"[{trace_log.id}]\n{trace_log.bot}\n{trace_log.event}\n"
                               f"Exception: {trace_log.exception}")
    else:
        await get_error.finish("未找到对应的错误记录")
