from datetime import datetime
import traceback

from nonebot import get_driver, require
from nonebot.adapters import Bot, Event
from nonebot.exception import FinishedException, MatcherException
from nonebot.log import logger

from .db import TraceLogOper, TraceSubOper

require("nonebot_plugin_htmlrender")
require("nonebot_plugin_orm")
require("nonebot_plugin_alconna")
require("nonebot_plugin_uninfo")

from nonebot_plugin_alconna import Target, UniMessage
from nonebot_plugin_htmlrender import template_to_pic
from nonebot_plugin_orm import get_session
from nonebot_plugin_uninfo import get_session as get_user_info

from .config import DATA_DIR, NICKNAME, PLUGIN_PATH, plugin_config
from .utils import generate_qr_code

driver = get_driver()
bot_qrcode_path, group_qrcode_path = None, None


@driver.on_startup
async def _startup():
    global bot_qrcode_path, group_qrcode_path
    if plugin_config.e_bot_link:
        bot_qrcode_path = generate_qr_code(
            data=str(plugin_config.e_bot_link), path=DATA_DIR / "img", filename="e_bot_link.png"
        )

    if plugin_config.e_bot_group_link:
        group_qrcode_path = generate_qr_code(
            data=str(plugin_config.e_bot_group_link), path=DATA_DIR / "img", filename="e_bot_group_link.png"
        )

    logger.info(f"二维码生成路径:\n机器人：{bot_qrcode_path}\n交流群：{group_qrcode_path}")


async def render_error(error_json: dict) -> bytes:
    templates_path = PLUGIN_PATH / "templates"

    image = await template_to_pic(
        template_path=templates_path,
        template_name="error.html.jinja2",
        templates=error_json,
        pages={
            "viewport": {"width": 1080, "height": 100},
            "base_url": f"file://{templates_path}",
        },
    )

    return image


async def handle_error(bot: Bot, event: Event, exception: Exception) -> str | None:
    """
    处理错误，生成错误图片并发送
    :param bot: nonebot Bot
    :param event: nonebot Event
    :param exception: 异常对象
    :return: 是否成功
    """
    if isinstance(exception, (MatcherException | FinishedException)):
        return None

    error_str = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))

    session = get_session()
    session.expire_on_commit = False

    async with session.begin():
        try:
            trace_log = TraceLogOper(session=session, bot=bot, event=event, exception=exception)
            trace_id = await trace_log.add()
            if not trace_id:
                trace_id = None

            error_json = {
                "e": str(exception),
                "event": str(event),
                "traceback": error_str,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "bot_link": bot_qrcode_path,
                "group_link": group_qrcode_path,
                "bot_id": bot.self_id,
                "nickname": NICKNAME if NICKNAME else "机器人",
                "trace_id": trace_id,
            }

            pic = await render_error(error_json)
            if not pic:
                logger.error("生成错误图片失败")
                return None
            else:
                msg = UniMessage.image(raw=pic)

            await msg.send(target=event, bot=bot)

            trace_sub_list = await TraceSubOper(session=session, user_info=await get_user_info(bot, event)).get_all()
            if trace_sub_list:
                for sub in trace_sub_list:
                    if str(bot.self_id) == str(sub.bot_id) and event.get_session_id() == sub.session_id:
                        continue
                    await msg.send(
                        target=Target(
                            self_id=sub.bot_id,
                            private=sub.session_type == "PRIVATE",
                            adapter=sub.adapter,
                            id=sub.session_id,
                        )
                    )
        except Exception:
            logger.error(f"处理错误时发生异常: {traceback.format_exc()}")
            await session.rollback()
            return None
        finally:
            await session.commit()
            return trace_id
